import argparse
import codecs
import datetime
import json
import logging
import os.path
import threading

from socket import error as SocketError
from socket import timeout
from ssl import SSLError
from urllib2 import URLError

import cLogger, cComments
import sys, os, time

from httplib import HTTPException
from instagram_private_api_extensions import live

class NoBroadcastException(Exception):
	pass

def main(apiArg, recordArg):
	global api
	global record
	global isRecording
	global currentDate
	currentDate = getDate()
	isRecording = False
	api = apiArg
	record = recordArg
	getUserInfo(record)

def recordStream(broadcast):
	try:
		def check_status():
			heartbeat_info = api.broadcast_heartbeat_and_viewercount(broadcast['id'])
			cLogger.log('[I] Broadcast status: %s' % heartbeat_info['broadcast_status'], "GREEN")
			return heartbeat_info['broadcast_status'] not in ['active', 'interrupted']

		mpd_url = (broadcast.get('dash_manifest')
				   or broadcast.get('dash_abr_playback_url')
				   or broadcast['dash_playback_url'])

		dl = live.Downloader(
			mpd=mpd_url,
			output_dir='{}_{}_{}_downloads/'.format(currentDate ,record, broadcast['id']),
			user_agent=api.user_agent,
			max_connection_error_retry=2,
			duplicate_etag_retry=60,
			callback_check=check_status,
			mpd_download_timeout=10,
			download_timeout=10)
	except Exception as e:
		cLogger.log('[E] Could not start recording broadcast: ' + str(e), "RED")
		cLogger.seperator("GREEN")
		sys.exit(0)

	try:
		viewers = broadcast.get('viewer_count', 0)
		started_mins, started_secs = divmod((int(time.time()) - broadcast['published_time']), 60)
		started_label = '%d minutes and ' % started_mins
		if started_secs:
			started_label += '%d seconds' % started_secs
		cLogger.log('[I] Starting broadcast recording:', "GREEN")
		cLogger.log('[I] Viewers: ' + str(int(viewers)) + " watching", "GREEN")
		cLogger.log('[I] Missing: ' + started_label, "GREEN")
		dl.run()
		stitchVideo(dl, broadcast)
	except KeyboardInterrupt:
		cLogger.log('', "GREEN")
		cLogger.log('[I] Aborting broadcast recording...', "GREEN")
		if not dl.is_aborted:
			dl.stop()
			stitchVideo(dl, broadcast)

def stitchVideo(dl, broadcast):
		isRecording = False
		cLogger.log('[I] Stitching downloaded files into video...', "GREEN")
		output_file = currentDate + "_" + record + "_" + str(broadcast['id']) + ".mp4"
		dl.stitch(output_file, cleartempfiles=False)
		cLogger.log('[I] Successfully stitched downloaded files!', "GREEN")
		cLogger.seperator("GREEN")
		sys.exit(0)

def getUserInfo(record):
	try:
		user_res = api.username_info(record)
		user_id = user_res['user']['pk']
		getBroadcast(user_id)
	except Exception as e:
		cLogger.log('[E] Could not get user info: ' + str(e), "RED")
		cLogger.seperator("GREEN")
		sys.exit(0)


def getBroadcast(user_id):
	try:
		cLogger.log('[I] Checking broadcast for "' + record + '"...', "GREEN")
		broadcast = api.user_broadcast(user_id)
		if (broadcast is None):
			raise NoBroadcastException('No broadcast available.')
		else:
			recordStream(broadcast)
	except NoBroadcastException as e:
		cLogger.log('[W] ' + str(e), "YELLOW")
		cLogger.seperator("GREEN")
		sys.exit(0)
	except Exception as e:
		if (e.__name__ is not NoBroadcastException):
			cLogger.log('[E] Could not get broadcast info: ' + str(e), "RED")
			cLogger.seperator("GREEN")
			sys.exit(0)

def getDate():
	return time.strftime("%Y%m%d")