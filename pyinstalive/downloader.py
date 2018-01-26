import sys
import time
import os
import shutil
import subprocess
import threading

from instagram_private_api_extensions import live, replay
from .logger import log, seperator

class NoLivestreamException(Exception):
	pass

class NoReplayException(Exception):
	pass

def main(api_arg, record_arg, settings_arg):
	global api
	global record
	global broadcast
	global mpd_url
	global settings
	settings = settings_arg
	api = api_arg
	record = record_arg
	get_user_info(record)

def run_script(file):
	try:
		FNULL = open(os.devnull, 'w')
		if sys.version.split(' ')[0].startswith('2'):
			subprocess.call(["python", file], stdout=FNULL, stderr=subprocess.STDOUT)
		else:
			subprocess.call(["python3", file], stdout=FNULL, stderr=subprocess.STDOUT)
	except OSError as e:
		pass

def get_stream_duration(broadcast):
	try:
		started_mins, started_secs = divmod((int(time.time()) - broadcast['published_time']), 60)
		started_label = '%d minutes' % started_mins
		if started_secs:
			started_label += ' and %d seconds' % started_secs
		return started_label
	except:
		return "not available"

def record_stream(broadcast):
	try:
		def print_status():
			heartbeat_info = api.broadcast_heartbeat_and_viewercount(broadcast['id'])
			viewers = broadcast.get('viewer_count', 0)
			log('[I] Viewers     : ' + str(int(viewers)) + " watching", "GREEN")
			log('[I] Airing time : ' + get_stream_duration(broadcast).title(), "GREEN")
			log('[I] Status      : ' + heartbeat_info['broadcast_status'].title(), "GREEN")
			seperator("GREEN")
			return heartbeat_info['broadcast_status'] not in ['active', 'interrupted'] 

		mpd_url = (broadcast.get('dash_manifest')
				   or broadcast.get('dash_abr_playback_url')
				   or broadcast['dash_playback_url'])

		output_dir = settings.save_path + '{}_{}_{}_{}_live_downloads'.format(settings.current_date, record, broadcast['id'], settings.current_time)

		dl = live.Downloader(
			mpd=mpd_url,
			output_dir=output_dir,
			user_agent=api.user_agent,
			max_connection_error_retry=3,
			duplicate_etag_retry=30,
			callback_check=print_status,
			mpd_download_timeout=5,
			download_timeout=10)
	except Exception as e:
		log('[E] Could not start recording livestream: ' + str(e), "RED")
		seperator("GREEN")
		sys.exit(1)
	try:
		log('[I] Starting livestream recording:', "GREEN")
		log('[I] Username    : ' + record, "GREEN")
		log('[I] MPD URL     : ' + mpd_url, "GREEN")
		print_status()
		log('[I] Recording livestream... press [CTRL+C] to abort.', "GREEN")

		if (settings.run_at_start is not "None"):
			try:
				thread = threading.Thread(target=run_script, args=(settings.run_at_start,))
				thread.daemon = True
				thread.start()
				log("[I] Executed file to run at start.", "GREEN")
			except Exception as e:
				log('[W] Could not run file: ' + str(e), "YELLOW")

		dl.run()
		log('[I] The livestream has ended. (Duration: ' + get_stream_duration(broadcast) + ")", "GREEN")
		stitch_video(dl, broadcast)
	except KeyboardInterrupt:
		log("", "GREEN")
		log('[W] Download has been aborted.', "YELLOW")
		log("", "GREEN")
		if not dl.is_aborted:
			dl.stop()
			stitch_video(dl, broadcast)

def stitch_video(dl, broadcast):
	if (settings.run_at_finish is not "None"):
		try:
			thread = threading.Thread(target=run_script, args=(settings.run_at_finish,))
			thread.daemon = True
			thread.start()
			log("[I] Executed file to run at finish.", "GREEN")
		except Exception as e:
			log('[W] Could not run file: ' + str(e), "YELLOW")

	log('[I] Stitching downloaded files into video...', "GREEN")
	output_file = settings.save_path + '{}_{}_{}_{}_live.mp4'.format(settings.current_date, record, broadcast['id'], settings.current_time)
	try:
		if settings.clear_temp_files.title() == "True":
			dl.stitch(output_file, cleartempfiles=True)
		else:
			dl.stitch(output_file, cleartempfiles=False)
		log('[I] Successfully stitched downloaded files.', "GREEN")
		seperator("GREEN")
		sys.exit(0)
	except Exception as e:
		log('[E] Could not stitch downloaded files: ' + str(e), "RED")
		seperator("GREEN")
		sys.exit(1)

def get_user_info(record):
	try:
		log("[I] Checking user: '"+ record + "'", "GREEN")
		user_res = api.username_info(record)
		user_id = user_res['user']['pk']
	except Exception as e:
		log('[E] Could not get user info: ' + str(e), "RED")
		seperator("GREEN")
		sys.exit(1)
	get_livestreams(user_id)
	if settings.save_replays.title() == "True": 
		get_replays(user_id)
	else:
		log("", "BLUE")
		log("[I] Replay saving is disabled either with a flag or in the config file.", "BLUE")
		seperator("GREEN")
		sys.exit(0)

def get_livestreams(user_id):
	try:
		log('[I] Checking for ongoing livestreams...', "GREEN")
		broadcast = api.user_broadcast(user_id)
		if (broadcast is None):
			raise NoLivestreamException('There are no livestreams available.')
		else:
			record_stream(broadcast)
	except NoLivestreamException as e:
		log('[W] ' + str(e), "YELLOW")
	except Exception as e:
		if (e.__class__.__name__ is not NoLivestreamException):
			log('[E] Could not get livestreams info: ' + str(e), "RED")
			seperator("GREEN")
			sys.exit(1)


def get_replays(user_id):
	try:
		log('[I] Checking for available replays...', "GREEN")
		user_story_feed = api.user_story_feed(user_id)
		broadcasts = user_story_feed.get('post_live_item', {}).get('broadcasts', [])
	except Exception as e:
		log('[E] Could not get replay info: ' + str(e), "RED")
		seperator("GREEN")
		sys.exit(1)
	try:
		if (len(broadcasts) == 0):
			raise NoReplayException('There are no replays available.')
		else:
			log("[I] Available replays have been found to download, press [CTRL+C] to abort.", "GREEN")
			log("", "GREEN")
			for index, broadcast in enumerate(broadcasts):
				exists = False

				if sys.version.split(' ')[0].startswith('2'):
					directories = (os.walk(settings.save_path).next()[1])
				else:
					directories = (os.walk(settings.save_path).__next__()[1])

				for directory in directories:
					if (str(broadcast['id']) in directory) and ("_live_" not in directory):
						log("[W] Already downloaded a replay with ID '" + str(broadcast['id']) + "', skipping...", "GREEN")
						exists = True
				if exists is False:
					current = index + 1
					log("[I] Downloading replay " + str(current) + " of "  + str(len(broadcasts)) + " with ID '" + str(broadcast['id']) + "'...", "GREEN")
					current_time = str(int(time.time()))
					output_dir = settings.save_path + '{}_{}_{}_{}_replay_downloads'.format(settings.current_date, record, broadcast['id'], settings.current_time)
					dl = replay.Downloader(
						mpd=broadcast['dash_manifest'],
						output_dir=output_dir,
						user_agent=api.user_agent)
					if settings.clear_temp_files.title() == "True":
						replay_saved = dl.download(settings.save_path + '{}_{}_{}_{}_replay.mp4'.format(settings.current_date, record, broadcast['id'], settings.current_time), cleartempfiles=True)
					else:
						replay_saved = dl.download(settings.save_path + '{}_{}_{}_{}_replay.mp4'.format(settings.current_date, record, broadcast['id'], settings.current_time), cleartempfiles=False)
					if (len(replay_saved) == 1):
						log("[I] Finished downloading replay " + str(current) + " of "  + str(len(broadcasts)) + ".", "GREEN")
						log("", "GREEN")
					else:
						log("[W] No output video file was made, please merge the files manually.", "RED")
						log("[W] Check if ffmpeg is available by running ffmpeg in your terminal.", "RED")
						log("", "GREEN")
		log("[I] Finished downloading available replays.", "GREEN")
		seperator("GREEN")
		sys.exit(0)
	except NoReplayException as e:
		log('[W] ' + str(e), "YELLOW")
		seperator("GREEN")
		sys.exit(0)
	except Exception as e:
		log('[E] Could not save replay: ' + str(e), "RED")
		seperator("GREEN")
		sys.exit(1)
	except KeyboardInterrupt:
		log("", "GREEN")
		log('[W] Download has been aborted.', "YELLOW")
		try:
			shutil.rmtree(output_dir)
		except Exception as e:
			log("[E] Could not remove temp folder: " + str(e), "RED")
			sys.exit(1)
		sys.exit(0)