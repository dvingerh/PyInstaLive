import json
import codecs
import datetime
import os.path
import logging
import argparse
import json
import codecs
from socket import timeout, error as SocketError
from ssl import SSLError
from urllib2 import URLError

from httplib import HTTPException
from instagram_private_api_extensions import live
import sys, os, time, json
import cLogger

class NoBroadcastException(Exception):
    pass

def main(apiArg, recordArg):
	global api
	global record
	api = apiArg
	record = recordArg
	getUserInfo(record)

def recordStream(broadcast):
    try:
        dl = live.Downloader(
            mpd=broadcast['dash_playback_url'],
            output_dir='{}_output_{}/'.format(record, broadcast['id']),
            user_agent=api.user_agent)
    except Exception as e:
        cLogger.log('[E] Could not start recording broadcast: ' + str(e), "RED")
        cLogger.seperator("GREEN")
        exit()

    try:
        cLogger.log('[I] Starting broadcast recording.', "GREEN")
        dl.run()
    except KeyboardInterrupt:
        cLogger.log('', "GREEN")
        cLogger.log('[I] Aborting broadcast recording.', "GREEN")
        if not dl.is_aborted:
            dl.stop()
    finally:
        t = time.time()
        cLogger.log('[I] Stitching downloaded files into video.', "GREEN")
        dl.stitch(record + "_" + str(broadcast['id']) + "_" + str(int(t)) + '.mp4')
        cLogger.log('[I] Successfully stitched downloaded files.', "GREEN")
        cLogger.seperator("GREEN")
        exit()


def getUserInfo(record):
    try:
        user_res = api.username_info(record)
        user_id = user_res['user']['pk']
        getBroadcast(user_id)
    except Exception as e:
        cLogger.log('[E] Could not get user info: ' + str(e), "RED")
        cLogger.seperator("GREEN")
        exit()


def getBroadcast(user_id):
    try:
        cLogger.log('[I] Checking broadcast for "' + record + '".', "GREEN")
        broadcast = api.user_broadcast(user_id)
        if (broadcast is None):
            raise NoBroadcastException('No broadcast available.')
        else:
        	recordStream(broadcast)
    except NoBroadcastException as e:
        cLogger.log('[W] ' + str(e), "YELLOW")
        cLogger.seperator("GREEN")
        exit()
    except Exception as e:
    	if (e.__name__ is not NoBroadcastException):
	        cLogger.log('[E] Could not get broadcast info: ' + str(e), "RED")
	        cLogger.seperator("GREEN")
	        exit()