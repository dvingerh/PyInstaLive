# -*- coding: utf-8 -*-

import time
import json
import codecs
import sys
from socket import timeout, error as SocketError
from ssl import SSLError
try:
	# py2
	from urllib2 import URLError
	from httplib import HTTPException
except ImportError:
	# py3
	from urllib.error import URLError
	from http.client import HTTPException

from instagram_private_api import ClientError
from .logger import log, seperator

"""
This feature of PyInstaLive was originally written by https://github.com/taengstagram
The code below and in downloader.py that's related to the comment downloading
feature is modified by https://github.com/notcammy
"""


class CommentsDownloader(object):

	def __init__(self, api, broadcast, destination_file):
		self.api = api
		self.broadcast = broadcast
		self.destination_file = destination_file
		self.comments = []

	def get_live(self, first_comment_created_at=0):
		comments_collected = self.comments

		before_count = len(comments_collected)
		try:
			comments_res = self.api.broadcast_comments(
				self.broadcast['id'], last_comment_ts=first_comment_created_at)
			comments = comments_res.get('comments', [])
			first_comment_created_at = (
				comments[0]['created_at_utc'] if comments else int(time.time() - 5))
			comments_collected.extend(comments)
			after_count = len(comments_collected)
			if after_count > before_count:
				broadcast = self.broadcast.copy()
				broadcast.pop('segments', None)     # save space
				broadcast['comments'] = comments_collected
				with open(self.destination_file, 'w') as outfile:
					json.dump(broadcast, outfile, indent=2)
			self.comments = comments_collected

		except (SSLError, timeout, URLError, HTTPException, SocketError) as e:
			log('[W] Comment downloading error: %s' % e, "YELLOW")
		except ClientError as e:
			if e.code == 500:
				log('[W] Comment downloading ClientError: %d %s' % (e.code, e.error_response), "YELLOW")
			elif e.code == 400 and not e.msg:
				log('[W] Comment downloading ClientError: %d %s' % (e.code, e.error_response), "YELLOW")
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
		encoding_tag = self.broadcast['encoding_tag']
		while True:
			comments_res = self.api.replay_broadcast_comments(
				self.broadcast['id'], starting_offset=starting_offset, encoding_tag=encoding_tag)
			starting_offset = comments_res.get('ending_offset', 0)
			comments = comments_res.get('comments', [])
			comments_collected.extend(comments)
			if not comments_res.get('comments') or not starting_offset:
				break
			time.sleep(4)

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
		subtitles_timeline = {}
		for i, c in enumerate(comments):
			if 'offset' in c:
				for k in c['comment'].keys():
					c[k] = c['comment'][k]
				c['created_at_utc'] = download_start_time + c['offset']
			created_at_utc = str(2 * (c['created_at_utc'] // 2))
			comment_list = subtitles_timeline.get(created_at_utc) or []
			comment_list.append(c)
			subtitles_timeline[created_at_utc] = comment_list

		if subtitles_timeline:
			timestamps = sorted(subtitles_timeline.keys())
			mememe = False
			subs = []
			for i, tc in enumerate(timestamps):
				t = subtitles_timeline[tc]
				clip_start = int(tc) - int(download_start_time) + int(comments_delay)
				if clip_start < 0:
					clip_start = 0

				log = ''
				for c in t:
						if (c['user']['is_verified']):
							log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(clip_start)), '{} {}: {}'.format(c['user']['username'], "(v)", c['text']))
						else:
							log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(clip_start)), '{}: {}'.format(c['user']['username'], c['text']))

				subs.append(log)

			with codecs.open(log_file, 'w', 'utf-8-sig') as log_outfile:
				log_outfile.write(''.join(subs))