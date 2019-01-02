# -*- coding: utf-8 -*-

import codecs
import json
import sys
import time
import os

from socket import error as SocketError
from socket import timeout
from ssl import SSLError

try:
    # py2
    from urllib2 import URLError
    from httplib import HTTPException
except ImportError:
    # py3
    from urllib.error import URLError
    from http.client import HTTPException


try:
    import logger
    import helpers
    import pil
    import dlfuncs
except ImportError:
    from . import logger
    from . import helpers
    from . import pil
    from . import dlfuncs

from instagram_private_api import ClientError

"""
The content of this file was originally written by https://github.com/taengstagram
The code has been edited for use in PyInstaLive.
"""


class CommentsDownloader(object):

    def __init__(self, destination_file):
        self.api = pil.ig_api
        self.broadcast = pil.livestream_obj
        self.destination_file = destination_file
        self.comments = []

    def get_live(self, first_comment_created_at=0):
        comments_collected = self.comments

        before_count = len(comments_collected)
        try:
            comments_res = self.api.broadcast_comments(
                self.broadcast.get('id'), last_comment_ts=first_comment_created_at)
            comments = comments_res.get('comments', [])
            first_comment_created_at = (
                comments[0]['created_at_utc'] if comments else int(time.time() - 5))
            comments_collected.extend(comments)
            after_count = len(comments_collected)
            if after_count > before_count:
                broadcast = self.broadcast.copy()
                broadcast.pop('segments', None)  # save space
                broadcast['comments'] = comments_collected
                with open(self.destination_file, 'w') as outfile:
                    json.dump(broadcast, outfile, indent=2)
            self.comments = comments_collected

        except (SSLError, timeout, URLError, HTTPException, SocketError) as e:
            logger.warn('Comment downloading error: %s' % e)
        except ClientError as e:
            if e.code == 500:
                logger.warn('Comment downloading ClientError: %d %s' % (e.code, e.error_response))
            elif e.code == 400 and not e.msg:
                logger.warn('Comment downloading ClientError: %d %s' % (e.code, e.error_response))
            else:
                raise e
        finally:
            try:
                time.sleep(4)
            except KeyboardInterrupt:
                return first_comment_created_at
        return first_comment_created_at

    def get_replay(self):
        comments_collected = []
        starting_offset = 0
        encoding_tag = self.broadcast.get('encoding_tag')
        while True:
            try:
                comments_res = self.api.replay_broadcast_comments(
                    self.broadcast.get('id'), starting_offset=starting_offset, encoding_tag=encoding_tag)
                starting_offset = comments_res.get('ending_offset', 0)
                comments = comments_res.get('comments', [])
                comments_collected.extend(comments)
                if not comments_res.get('comments') or not starting_offset:
                    break
                time.sleep(4)
            except Exception:
                pass

        if comments_collected:
            self.broadcast['comments'] = comments_collected
            self.broadcast['initial_buffered_duration'] = 0
            with open(self.destination_file, 'w') as outfile:
                json.dump(self.broadcast, outfile, indent=2)
        self.comments = comments_collected

    def save(self):
        broadcast = self.broadcast.copy()
        broadcast.pop('segments', None)
        broadcast['comments'] = self.comments
        with open(self.destination_file, 'w') as outfile:
            json.dump(broadcast, outfile, indent=2)

    @staticmethod
    def generate_log(comments, download_start_time, log_file, comments_delay=10.0):
        python_version = sys.version.split(' ')[0]
        comments_timeline = {}
        wide_build = sys.maxunicode > 65536
        for i, c in enumerate(comments):
            if 'offset' in c:
                for k in c.get('comment').keys():
                    c[k] = c.get('comment', {}).get(k)
                c['created_at_utc'] = download_start_time + c.get('offset')
            created_at_utc = str(2 * (c.get('created_at_utc') // 2))
            comment_list = comments_timeline.get(created_at_utc) or []
            comment_list.append(c)
            comments_timeline[created_at_utc] = comment_list

        if comments_timeline:
            comment_errors = 0
            total_comments = 0
            timestamps = sorted(comments_timeline.keys())
            subs = []
            for i, tc in enumerate(timestamps):
                t = comments_timeline[tc]
                clip_start = int(tc) - int(download_start_time) + int(comments_delay)
                if clip_start < 0:
                    clip_start = 0

                comments_log = ''
                for c in t:
                    try:
                        if python_version.startswith('3'):
                            if c.get('user', {}).get('is_verified'):
                                comments_log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(clip_start)),
                                                                  '{} {}: {}'.format(c.get('user', {}).get('username'),
                                                                                     "(v)", c.get('text')))
                            else:
                                comments_log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(clip_start)),
                                                                  '{}: {}'.format(c.get('user', {}).get('username'),
                                                                                  c.get('text')))
                        else:
                            if not wide_build:
                                if c.get('user', {}).get('is_verified'):
                                    comments_log += '{}{}\n\n'.format(
                                        time.strftime('%H:%M:%S\n', time.gmtime(clip_start)),
                                        '{} {}: {}'.format(c.get('user', {}).get('username'), "(v)",
                                                           c.get('text').encode('ascii', 'ignore')))
                                else:
                                    comments_log += '{}{}\n\n'.format(
                                        time.strftime('%H:%M:%S\n', time.gmtime(clip_start)),
                                        '{}: {}'.format(c.get('user', {}).get('username'),
                                                        c.get('text').encode('ascii', 'ignore')))
                            else:
                                if c.get('user', {}).get('is_verified'):
                                    comments_log += '{}{}\n\n'.format(
                                        time.strftime('%H:%M:%S\n', time.gmtime(clip_start)),
                                        '{} {}: {}'.format(c.get('user', {}).get('username'), "(v)", c.get('text')))
                                else:
                                    comments_log += '{}{}\n\n'.format(
                                        time.strftime('%H:%M:%S\n', time.gmtime(clip_start)),
                                        '{}: {}'.format(c.get('user', {}).get('username'), c.get('text')))
                    except Exception:
                        comment_errors += 1
                        try:
                            if c.get('user', {}).get('is_verified'):
                                comments_log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(clip_start)),
                                                                  '{} {}: {}'.format(c.get('user', {}).get('username'),
                                                                                     "(v)",
                                                                                     c.get('text').encode('ascii',
                                                                                                          'ignore')))
                            else:
                                comments_log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(clip_start)),
                                                                  '{}: {}'.format(c.get('user', {}).get('username'),
                                                                                  c.get('text').encode('ascii',
                                                                                                       'ignore')))
                        except Exception:
                            pass
                total_comments += 1
                subs.append(comments_log)

            with codecs.open(log_file, 'w', 'utf-8-sig') as log_outfile:
                if python_version.startswith('2') and not wide_build:
                    log_outfile.write(
                        'This log was generated using Python {:s} without wide unicode support. This means characters '
                        'such as emotes are not saved.\nUser comments without any text usually are comments that only '
                        'had emotes.\nBuild Python 2 with the --enable-unicode=ucs4 argument or use Python 3 for full '
                        'unicode support.\n\n'.format(
                            python_version) + ''.join(subs))
                else:
                    log_outfile.write(''.join(subs))
            return comment_errors, total_comments
