import sys
import time

from instagram_private_api_extensions import live

import logger


class NoBroadcastException(Exception):
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

		output_dir = save_path + '{}_{}_{}_{}_downloads'.format(current_date, record, broadcast['id'], current_time)

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
		logger.log('[E] Could not start recording broadcast: ' + str(e), "RED")
		logger.seperator("GREEN")
		sys.exit(0)

	try:
		viewers = broadcast.get('viewer_count', 0)
		started_mins, started_secs = divmod((int(time.time()) - broadcast['published_time']), 60)
		started_label = '%d minutes and ' % started_mins
		if started_secs:
			started_label += '%d seconds' % started_secs
		logger.log('[I] Starting broadcast recording:', "GREEN")
		last_stream = open("last_stream.html", "w")
		last_stream.write('<b>Username:</b> {}<br><b>MPD URL:</b> <a href="{}">LINK</a><br><b>Viewers:</b> {}<br><b>Missing:</b> {}'
			.format(record, mpd_url, str(int(viewers)), started_label))
		last_stream.close()
		logger.log('[I] Username    : ' + record, "GREEN")
		logger.log('[I] MPD URL     : ' + mpd_url, "GREEN")
		print_status(api, broadcast)
		logger.log('[I] Recording broadcast... press [CTRL+C] to abort.', "GREEN")
		dl.run()
		stitch_video(dl, broadcast)
	except KeyboardInterrupt:
		logger.log('', "GREEN")
		logger.log('[I] Aborting broadcast recording...', "GREEN")
		if not dl.is_aborted:
			dl.stop()
			stitch_video(dl, broadcast)

def stitch_video(dl, broadcast):
		logger.log('[I] Stitching downloaded files into video...', "GREEN")
		output_file = save_path + '{}_{}_{}_{}.mp4'.format(current_date, record, broadcast['id'], current_time)
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
		get_broadcast(user_id)
	except Exception as e:
		logger.log('[E] Could not get user info for "' + record + '" : ' + str(e), "RED")
		logger.seperator("GREEN")
		sys.exit(0)


def get_broadcast(user_id):
	try:
		logger.log('[I] Checking broadcast for "' + record + '"...', "GREEN")
		broadcast = api.user_broadcast(user_id)
		if (broadcast is None):
			raise NoBroadcastException('No broadcast available.')
		else:
			record_stream(broadcast)
	except NoBroadcastException as e:
		logger.log('[W] ' + str(e), "YELLOW")
		logger.seperator("GREEN")
		sys.exit(0)
	except Exception as e:
		if (e.__name__ is not NoBroadcastException):
			logger.log('[E] Could not get broadcast info: ' + str(e), "RED")
			logger.seperator("GREEN")
			sys.exit(0)

def print_status(api, broadcast):
	heartbeat_info = api.broadcast_heartbeat_and_viewercount(broadcast['id'])
	viewers = broadcast.get('viewer_count', 0)
	started_mins, started_secs = divmod((int(time.time()) - broadcast['published_time']), 60)
	started_label = '%d minutes and ' % started_mins
	if started_secs:
		started_label += '%d seconds' % started_secs
	logger.log('[I] Viewers     : ' + str(int(viewers)) + " watching", "GREEN")
	logger.log('[I] Airing time : ' + started_label, "GREEN")
	logger.log('[I] Status      : ' + heartbeat_info['broadcast_status'].title(), "GREEN")
	logger.log('', "GREEN")