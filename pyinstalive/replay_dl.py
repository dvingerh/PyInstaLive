# Copyright (c) 2017 https://github.com/ping
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import argparse
import logging
import os
import re
import xml.etree.ElementTree
import subprocess
from contextlib import closing

import requests


logger = logging.getLogger(__file__)


MPD_NAMESPACE = {'mpd': 'urn:mpeg:dash:schema:mpd:2011'}


class Downloader(object):
    """Downloads and assembles a given IG live replay stream"""

    USER_AGENT = 'Instagram 10.26.0 (iPhone8,1; iOS 10_2; en_US; en-US; ' \
                 'scale=2.00; gamut=normal; 750x1334) AppleWebKit/420+'
    DOWNLOAD_TIMEOUT = 15

    def __init__(self, mpd, output_dir, user_agent=None, **kwargs):
        """
        :param mpd: URL to mpd
        :param output_dir: folder to store the downloaded files
        :return:
        """
        self.mpd = mpd
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.user_agent = user_agent or self.USER_AGENT
        self.download_timeout = kwargs.pop('download_timeout', None) or self.DOWNLOAD_TIMEOUT

        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=2)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        self.session = session

        # custom ffmpeg binary path, fallback to ffmpeg_binary path in env if available
        self.ffmpeg_binary = kwargs.pop('ffmpeg_binary', None) or os.getenv('FFMPEG_BINARY', 'ffmpeg')

        xml.etree.ElementTree.register_namespace('', MPD_NAMESPACE['mpd'])
        self.mpd_document = xml.etree.ElementTree.fromstring(self.mpd)

        duration_attribute = self.mpd_document.attrib.get('mediaPresentationDuration', '')
        mobj = re.match(r'PT(?P<hrs>\d+)H(?P<mins>\d+)M(?P<secs>\d+\.\d+)', duration_attribute)
        if mobj:
            duration = int(round(
                int(mobj.group('hrs')) * 60 * 60 +
                int(mobj.group('mins')) * 60 +
                float(mobj.group('secs'))
            ))
        else:
            logger.warning('Unable to parse duration: {}'.format(duration_attribute))
            duration = 0
        self.duration = duration

    def download(self, output_filename,
                 skipffmpeg=False,
                 cleartempfiles=True):
        """
        Download and saves the generated file with the file name specified.
        :param output_filename: Output file path
        :param skipffmpeg: bool flag to not use ffmpeg to join audio and video file into final mp4
        :param cleartempfiles: bool flag to remove downloaded and temp files
        :return:
        """

        periods = self.mpd_document.findall('mpd:Period', MPD_NAMESPACE)
        logger.debug('Found {0:d} period(s)'.format(len(periods)))

        generated_files = []

        # Aaccording to specs, multiple periods are allow but IG only sends one usually
        for period_idx, period in enumerate(periods):
            adaptation_sets = period.findall('mpd:AdaptationSet', MPD_NAMESPACE)
            audio_stream = None
            video_stream = None
            if not len(adaptation_sets) == 2:
                logger.warning('Unexpected number of adaptation sets: {}'.format(len(adaptation_sets)))
            for adaptation_set in adaptation_sets:
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
                mime_type = representation.attrib.get('mimeType', '')
                logger.debug(
                    'Selected representation with mimeType {0!s} id {1!s} out of {2!s}'.format(
                        mime_type,
                        representation_id,
                        ' / '.join([r.attrib.get('id', '') for r in representations])
                    ))
                representation_base_url = representation.find('mpd:BaseURL', MPD_NAMESPACE).text
                logger.debug(representation_base_url)
                if 'video' in mime_type and not video_stream:
                    video_stream = representation_base_url
                elif 'audio' in mime_type and not audio_stream:
                    audio_stream = representation_base_url

                if audio_stream and video_stream:
                    break

            audio_file = (os.path.join(self.output_dir, os.path.basename(audio_stream))).split('?')[0]
            video_file = (os.path.join(self.output_dir, os.path.basename(video_stream))).split('?')[0]
            for target in ((audio_stream, audio_file), (video_stream, video_file)):
                logger.debug('Downloading {} as {}'.format(*target))
                with closing(self.session.get(
                        target[0],
                        headers={'User-Agent': self.user_agent, 'Accept': '*/*'},
                        timeout=self.download_timeout, stream=True)) as res:
                    res.raise_for_status()

                    with open(target[1], 'wb') as f:
                        for chunk in res.iter_content(chunk_size=1024*100):
                            f.write(chunk)

            if skipffmpeg:
                continue

            if len(periods) > 1:
                # Generate a new filename by appending n+1
                # to the original specified output filename
                # so that it looks like output-1.mp4, output-2.mp4, etc
                dir_name = os.path.dirname(output_filename)
                file_name = os.path.basename(output_filename)
                dot_pos = file_name.rfind('.')
                if dot_pos >= 0:
                    filename_no_ext = file_name[0:dot_pos]
                    ext = file_name[dot_pos:]
                else:
                    filename_no_ext = file_name
                    ext = ''
                generated_filename = os.path.join(
                    dir_name, '{0!s}-{1:d}{2!s}'.format(filename_no_ext, period_idx + 1, ext))
            else:
                generated_filename = output_filename

            ffmpeg_loglevel = 'error'
            if logger.level == logging.DEBUG:
                ffmpeg_loglevel = 'warning'

            cmd = [
                self.ffmpeg_binary, '-y',
                '-loglevel', ffmpeg_loglevel,
                '-i', audio_file,
                '-i', video_file,
                '-c:v', 'copy',
                '-c:a', 'copy',
                generated_filename]

            try:
                exit_code = subprocess.call(cmd)
                if exit_code:
                    logger.error('ffmpeg exited with the code: {0!s}'.format(exit_code))
                    logger.error('Command: {0!s}'.format(' '.join(cmd)))
                    continue
            except Exception as call_err:
                logger.error('ffmpeg exited with the error: {0!s}'.format(call_err))
                logger.error('Command: {0!s}'.format(' '.join(cmd)))
                continue

            generated_files.append(generated_filename)
            logger.debug('Generated {}'.format(generated_filename))
            if cleartempfiles:
                for f in (audio_file, video_file):
                    try:
                        os.remove(f)
                    except (IOError, OSError) as ioe:
                        logger.warning('Error removing {0!s}: {1!s}'.format(f, str(ioe)))

        return generated_files


if __name__ == '__main__':      # pragma: no cover

    # pylint: disable-all

    # Example of how to init and start the Downloader
    parser = argparse.ArgumentParser()
    parser.add_argument('mpd')
    parser.add_argument('-v', action='store_true', help='Verbose')
    parser.add_argument('-s', metavar='OUTPUT_FILENAME', required=True,
                        help='Output filename')
    parser.add_argument('-o', metavar='DOWLOAD_DIR',
                        default='output/', help='Download folder')
    parser.add_argument('-c', action='store_true', help='Clear temp files')
    args = parser.parse_args()

    if args.v:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logging.basicConfig(level=logger.level)

    with open(args.mpd, 'r') as mpd_file:
        mpd_contents = mpd_file.read()
        dl = Downloader(mpd=mpd_contents, output_dir=args.o)
        try:
            generated_files = dl.download(args.s, cleartempfiles=args.c)
            print('Video Duration: %s' % dl.duration)
            print('Generated files: \n%s' % '\n'.join(generated_files))
        except KeyboardInterrupt as e:
            logger.info('Interrupted')