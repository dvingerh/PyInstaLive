import sys
import time
import os

from instagram_private_api_extensions import live, replay

import logger


class NoLivestreamException(Exception):
	pass

class NoReplayException(Exception):
	pass

def main(api_arg, record_arg, save_path_arg):
	global api
	global record
	global save_path
	global current_date
	global current_time
	global broadcast
	global mpd_url
	current_time = str(int(time.time()))
	current_date = time.strftime("%Y%m%d")
	api = api_arg
	record = record_arg
	save_path = save_path_arg
	get_user_info(record)

def record_stream(broadcast):
	try:
		def check_status():
			print_status()

		mpd_url = (broadcast.get('dash_manifest')
				   or broadcast.get('dash_abr_playback_url')
				   or broadcast['dash_playback_url'])

		output_dir = save_path + '{}_{}_{}_{}_live_downloads'.format(current_date, record, broadcast['id'], current_time)

		dl = live.Downloader(
			mpd=mpd_url,
			output_dir=output_dir,
			user_agent=api.user_agent,
			max_connection_error_retry=2,
			duplicate_etag_retry=60,
			callback_check=check_status,
			mpd_download_timeout=10,
			download_timeout=10)
	except Exception as e:
		logger.log('[E] Could not start recording livestream: ' + str(e), "RED")
		logger.seperator("GREEN")
		sys.exit(0)
	try:
		logger.log('[I] Starting livestream recording:', "GREEN")
		logger.log('[I] Username    : ' + record, "GREEN")
		logger.log('[I] MPD URL     : ' + mpd_url, "GREEN")
		print_status(api, broadcast)
		logger.log('[I] Recording livestream... press [CTRL+C] to abort.', "GREEN")
		dl.run()
		stitch_video(dl, broadcast)
	except KeyboardInterrupt:
		logger.log('', "GREEN")
		logger.log('[I] Aborting livestream recording...', "GREEN")
		if not dl.is_aborted:
			dl.stop()
			stitch_video(dl, broadcast)

def stitch_video(dl, broadcast):
		logger.log('[I] Stitching downloaded files into video...', "GREEN")
		output_file = save_path + '{}_{}_{}_{}_live.mp4'.format(current_date, record, broadcast['id'], current_time)
		try:
			dl.stitch(output_file, cleartempfiles=False)
			logger.log('[I] Successfully stitched downloaded files!', "GREEN")
			logger.seperator("GREEN")
			sys.exit(0)
		except Exception as e:
			logger.log('[E] Could not stitch downloaded files: ' + str(e), "RED")
			logger.seperator("GREEN")
			sys.exit(0)

def get_user_info(record):
	try:
		user_res = api.username_info(record)
		user_id = user_res['user']['pk']
		get_livestreams(user_id)
	except Exception as e:
		logger.log('[E] Could not get livestream info for "' + record + '" : ' + str(e), "RED")
		logger.seperator("GREEN")
		sys.exit(0)
	get_replays(user_id)

def get_livestreams(user_id):
	try:
		logger.log('[I] Checking livestreams for "' + record + '"...', "GREEN")
		broadcast = api.user_broadcast(user_id)
		if (broadcast is None):
			raise NoLivestreamException('No livestreams available.')
		else:
			record_stream(broadcast)
	except NoLivestreamException as e:
		logger.log('[W] ' + str(e), "YELLOW")
	except Exception as e:
		if (e.__class__.__name__ is not NoLivestreamException):
			logger.log('[E] Could not get livestreams info: ' + str(e), "RED")
			logger.seperator("GREEN")
			sys.exit(0)


def get_replays(user_id):
	try:
		user_story_feed = api.user_story_feed(user_id)
		broadcasts = user_story_feed.get('post_live_item', {}).get('broadcasts', [])
		if (len(broadcasts) == 0):
			raise NoReplayException('No replays available.')
		else:
			for index, broadcast in enumerate(broadcasts):
				exists = False
				print(save_path)
				for directory in (os.walk(save_path).next()[1]):
					print(directory)
					if (str(broadcast['id']) in directory) and ("_live_" not in directory):
						logger.log("[W] Already downloaded a replay with ID '" + str(broadcast['id']) + "', skipping...", "GREEN")
					exists = True
					return
				if exists is False:
					current = index + 1
					logger.log("[I] Starting replay download " + str(current) + " of "  + str(len(broadcasts)) + "...", "GREEN")
					current_time = str(int(time.time()))
					output_dir = save_path + '{}_{}_{}_{}_replay_downloads'.format(current_date, record, broadcast['id'], current_time)
					dl = replay.Downloader(
						mpd=broadcast['dash_manifest'],
						output_dir=output_dir,
						user_agent=api.user_agent)
				dl.download(save_path + '{}_{}_{}_{}_replay.mp4'.format(current_date, record, broadcast['id'], current_time), cleartempfiles=False)
			logger.log("[I] Finished downloading available replays.", "GREEN")
			logger.seperator("GREEN")
			sys.exit(0)
	except NoReplayException as e:
		logger.log('[W] ' + str(e), "YELLOW")
		logger.seperator("GREEN")
		sys.exit(0)
	except Exception as e:
		if (e.__class__.__name__ is not NoReplayException):
			logger.log('[E] Could not get replay info: ' + str(e), "RED")
			logger.seperator("GREEN")
			sys.exit(0)

def print_status(api, broadcast):
	heartbeat_info = api.broadcast_heartbeat_and_viewercount(broadcast['id'])
	viewers = broadcast.get('viewer_count', 0)
	started_mins, started_secs = divmod((int(time.time()) - broadcast['published_time']), 60)
	started_label = '%d minutes' % started_mins
	if started_secs:
		started_label += ' and %d seconds' % started_secs
	logger.log('[I] Viewers     : ' + str(int(viewers)) + " watching", "GREEN")
	logger.log('[I] Airing time : ' + started_label, "GREEN")
	logger.log('[I] Status      : ' + heartbeat_info['broadcast_status'].title(), "GREEN")
	logger.log('', "GREEN")