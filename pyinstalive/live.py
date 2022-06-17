# Copyright (c) 2017 https://github.com/ping
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import logging
import os
import time
import re
import hashlib
import xml.etree.ElementTree
import threading
import shutil
import subprocess

from . import globals

import requests
import urllib.parse as compat_urlparse




logger = logging.getLogger(__file__)


MPD_NAMESPACE = {'mpd': 'urn:mpeg:dash:schema:mpd:2011'}


class Downloader(object):
    """Downloads and assembles a given IG live stream"""
    DOWNLOAD_TIMEOUT = 15
    DUPLICATE_ETAG_RETRY = 30
    MAX_CONNECTION_ERROR_RETRY = 10
    SLEEP_INTERVAL_BEFORE_RETRY = 5

    def __init__(self, mpd, output_dir, callback_check=None, singlethreaded=False, **kwargs):
        """
        :param mpd: URL to mpd
        :param output_dir: folder to store the downloaded files
        :param callback_check: callback function that can be used to check
            on stream status if the downloader cannot be sure that the stream
            is over
        :param singlethreaded: flag to force single threaded downloads.
            Not advisable since this increases the probability of lost segments.
        :return:
        """
        self.mpd = mpd
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.threads = []
        self.downloaders = {}
        self.last_etag = ''
        self.duplicate_etag_count = 0
        self.callback = callback_check
        self.is_aborted = False
        self.singlethreaded = singlethreaded
        self.stream_id = ''
        self.segment_meta = {}
        self.mpd_download_timeout = kwargs.pop('mpd_download_timeout', None) or self.MPD_DOWNLOAD_TIMEOUT
        self.download_timeout = kwargs.pop('download_timeout', None) or self.DOWNLOAD_TIMEOUT
        self.duplicate_etag_retry = kwargs.pop('duplicate_etag_retry', None) or self.DUPLICATE_ETAG_RETRY
        self.max_connection_error_retry = (kwargs.pop('max_connection_error_retry', None)
                                           or self.MAX_CONNECTION_ERROR_RETRY)
        self.sleep_interval_before_retry = (kwargs.pop('sleep_interval_before_retry', None)
                                            or self.SLEEP_INTERVAL_BEFORE_RETRY)

        session = globals.session.session

        adapter = requests.adapters.HTTPAdapter(max_retries=2, pool_maxsize=25)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        self.session = session

        # to store the duration of the initial buffered sgements available
        self.initial_buffered_duration = 0.0

    def _store_segment_meta(self, segment, representation):
        if segment not in self.segment_meta:
            self.segment_meta[segment] = representation

    def run(self):
        """Begin downloading"""
        connection_retries_count = 0
        while not self.is_aborted:
            try:
                mpd, wait = self._download_mpd()
                connection_retries_count = 0    # reset count

                if not self.duplicate_etag_count:
                    self._process_mpd(mpd)
                else:
                    logger.debug('Skip mpd processing: {0:d} - {1!s}'.format(
                        self.duplicate_etag_count, self.last_etag))
                if wait:
                    logger.debug('Sleeping for {0:d}s'.format(wait))
                    time.sleep(wait)

            except requests.HTTPError as e:
                err_msg = 'HTTPError downloading {0!s}: {1!s}.'.format(self.mpd, e)
                if e.response is not None and \
                        (e.response.status_code >= 500 or e.response.status_code == 404):
                    # 505 - temporal server problem
                    # 404 - seems to indicate that stream is starting but not ready
                    # 403 - stream is too long gone
                    connection_retries_count += 1
                    if connection_retries_count <= self.max_connection_error_retry:
                        logger.warning(err_msg)
                        time.sleep(self.sleep_interval_before_retry)
                    else:
                        logger.error(err_msg)
                        self.is_aborted = True
                else:
                    logger.error(err_msg)
                    self.is_aborted = True
            except requests.ConnectionError as e:
                # transient error maybe?
                connection_retries_count += 1
                if connection_retries_count <= self.max_connection_error_retry:
                    logger.warning('ConnectionError downloading {0!s}: {1!s}. Retrying...'.format(self.mpd, e))
                else:
                    logger.error('ConnectionError downloading {0!s}: {1!s}.'.format(self.mpd, e))
                    self.is_aborted = True

        self.stop()

    def stop(self):
        """
        This is usually called automatically by the downloader but if the download process is
        interrupted unexpectedly, e.g. KeyboardInterrupt, you should call this method to gracefully
        close off the download.

        :return:
        """
        self.is_aborted = True
        if not self.singlethreaded:
            logger.debug('Stopping download threads...')
            threads = self.downloaders.values()
            logger.debug('{0:d} of {1:d} threads are alive'.format(
                len([t for t in threads if t and t.is_alive()]),
                len(threads)))
            [t.join() for t in threads if t and t.is_alive()]

    def _download_mpd(self):
        """Downloads the mpd stream info and returns the xml object."""
        logger.debug('Requesting {0!s}'.format(self.mpd))
        res = self.session.get(self.mpd, headers={
            'Accept': '*/*',
        }, timeout=self.mpd_download_timeout)
        res.raise_for_status()

        # IG used to send this header when the broadcast ended.
        # Leaving it in in case it returns.
        broadcast_ended = res.headers.get('X-FB-Video-Broadcast-Ended', '')
        # Use the cache-control header as indicator that stream has ended
        cache_control = res.headers.get('Cache-Control', '')
        mobj = re.match(r'max\-age=(?P<age>[0-9]+)', cache_control)
        if mobj:
            max_age = int(mobj.group('age'))
        else:
            max_age = 0

        # Use ETag to detect if the same mpd is received repeatedly
        # if missing, use contents hash as psuedo etag
        etag = res.headers.get('ETag') or hashlib.md5(res.content).hexdigest()
        if etag != self.last_etag:
            self.last_etag = etag
            self.duplicate_etag_count = 0
        else:
            self.duplicate_etag_count += 1

        if broadcast_ended:
            logger.debug('Found X-FB-Video-Broadcast-Ended header: {0!s}'.format(broadcast_ended))
            logger.info('Stream ended.')
            self.is_aborted = True
        elif max_age > 1:
            logger.info('Stream ended (cache-control: {0!s}).'.format(cache_control))
            self.is_aborted = True
        else:
            # Periodically check callback if duplicate etag is detected
            if self.duplicate_etag_count and (self.duplicate_etag_count % 5 == 0):
                logger.warning('Duplicate etag {0!s} detected {1:d} time(s)'.format(
                    etag, self.duplicate_etag_count))
                if self.callback:
                    callback = self.callback
                    try:
                        abort = callback()
                        if abort:
                            logger.debug('Callback returned True')
                            self.is_aborted = True
                    except Exception as e:      # pylint: disable=broad-except
                        logger.warning('Error from callback: {0!s}'.format(str(e)))
            # Final hard abort
            elif self.duplicate_etag_count >= self.duplicate_etag_retry:
                logger.info('Stream likely ended (duplicate etag/hash detected).')
                self.is_aborted = True

        xml.etree.ElementTree.register_namespace('', MPD_NAMESPACE['mpd'])
        mpd = xml.etree.ElementTree.fromstring(res.text)
        minimum_update_period = mpd.attrib.get('minimumUpdatePeriod', '')
        mobj = re.match('PT(?P<secs>[0-9]+)S', minimum_update_period)
        if mobj:
            after = int(mobj.group('secs'))
        else:
            after = 1
        return mpd, after

    def _process_mpd(self, mpd):
        periods = mpd.findall('mpd:Period', MPD_NAMESPACE)
        logger.debug('Found {0:d} period(s)'.format(len(periods)))
        # Aaccording to specs, multiple periods are allow but IG only sends one usually
        for period in periods:
            logger.debug('Processing period {0!s}'.format(period.attrib.get('id')))
            for adaptation_set in period.findall('mpd:AdaptationSet', MPD_NAMESPACE):
                representations = adaptation_set.findall('mpd:Representation', MPD_NAMESPACE)
                # sort representations by quality and pick best one
                representations = sorted(
                    representations,
                    key=lambda rep: (
                        (int(rep.attrib.get('width', '0')) * int(rep.attrib.get('height', '0'))) or
                        int(rep.attrib.get('bandwidth', '0')) or
                        rep.attrib.get('FBQualityLabel') or
                        int(rep.attrib.get('audioSamplingRate', '0'))),
                    reverse=True)
                representation = representations[0]
                representation_id = representation.attrib.get('id', '')
                logger.debug(
                    'Selected representation with id {0!s} out of {1!s}'.format(
                        representation_id,
                        ' / '.join([r.attrib.get('id', '') for r in representations])
                    ))

                representation_label = ''
                # only store segments meta for video
                if 'video' in representation.attrib.get('mimeType', ''):
                    if representation.attrib.get('FBQualityLabel'):
                        representation_label = representation.attrib.get('FBQualityLabel')
                    elif representation.attrib.get('width') and representation.attrib.get('height'):
                        representation_label = '{0!s}x{1!s}'.format(
                            representation.attrib.get('width'),
                            representation.attrib.get('height'))
                    elif representation_id:
                        representation_label = representation_id

                segment_template = representation.find('mpd:SegmentTemplate', MPD_NAMESPACE)

                init_segment = segment_template.attrib.get('initialization')
                media_name = segment_template.attrib.get('media')
                timescale = int(segment_template.attrib.get('timescale'))

                # store stream ID
                if not self.stream_id:
                    mobj = re.search(r'\b(?P<id>[0-9_]+)\-init', init_segment)
                    if mobj:
                        self.stream_id = mobj.group('id')

                # download timeline segments
                segment_timeline = segment_template.find('mpd:SegmentTimeline', MPD_NAMESPACE)
                segments = segment_timeline.findall('mpd:S', MPD_NAMESPACE)

                buffered_duration = 0
                for i, seg in enumerate(segments):
                    buffered_duration += int(seg.attrib.get('d'))
                    seg_filename = media_name.replace(
                        '$Time$', seg.attrib.get('t')).replace('$RepresentationID$', representation_id)
                    segment_url = compat_urlparse.urljoin(self.mpd, seg_filename)

                    if representation_label:
                        self._store_segment_meta(
                            os.path.basename(compat_urlparse.urlparse(seg_filename).path), representation_label)

                    # Append init chunk to first segment in the timeline for now
                    # Not sure if it's needed for every segment yet
                    init_chunk = None
                    if i == 0:
                        # download init segment
                        init_segment_url = compat_urlparse.urljoin(self.mpd, init_segment)
                        init_chunk = self._download(
                            init_segment_url, None, timeout=self.mpd_download_timeout)

                    self._extract(
                        os.path.basename(seg_filename),
                        segment_url,
                        os.path.join(
                            self.output_dir,
                            os.path.basename(
                                compat_urlparse.urlparse(seg_filename).path)
                        ),
                        init_chunk=init_chunk)

                if not self.initial_buffered_duration:
                    self.initial_buffered_duration = float(buffered_duration) / timescale
                    logger.debug('Initial buffered duration: {0!s}'.format(self.initial_buffered_duration))

    def _extract(self, identifier, target, output, init_chunk=None):
        if identifier in self.downloaders:
            logger.debug('Already downloading {0!s}'.format(identifier))
            return
        logger.debug('Requesting {0!s}'.format(target))
        if self.singlethreaded:
            self._download(target, output, init_chunk=init_chunk)
        else:
            # push each download into it's own thread
            t = threading.Thread(
                target=self._download, name=identifier,
                kwargs={'target': target, 'output': output, 'init_chunk': init_chunk})
            t.start()
            self.downloaders[identifier] = t

    def _download(self, target, output, timeout=None, init_chunk=None):
        retry_attempts = self.max_connection_error_retry + 1
        for i in range(1, retry_attempts + 1):
            try:
                res = self.session.get(target, headers={
                    'Accept': '*/*',
                }, timeout=timeout or self.download_timeout)
                res.raise_for_status()

                if not output:
                    return res.content

                with open(output, 'wb') as f:
                    if init_chunk:
                        # prepend init chunk
                        logger.debug('Appended chunk len {0:d} to {1!s}'.format(
                            len(init_chunk), output))
                        f.write(init_chunk)
                    f.write(res.content)
                return
            except (requests.HTTPError, requests.ConnectionError) as e:
                if isinstance(e, requests.HTTPError):
                    err_msg = 'HTTPError {0:d} {1!s}: {2!s}.'.format(e.response.status_code, target, e)
                else:
                    err_msg = 'ConnectionError {0!s}: {1!s}'.format(target, e)
                if i < retry_attempts:
                    logger.warning('{0!s}. Retrying... '.format(err_msg))
                else:
                    logger.error(err_msg)

    @staticmethod
    def _get_file_index(filename):
        """ Extract the numbered index in filename for sorting """
        mobj = re.match(r'.+\-(?P<idx>[0-9]+)\.[a-z]+', filename)
        if mobj:
            return int(mobj.group('idx'))
        return -1
