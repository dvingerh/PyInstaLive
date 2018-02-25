import sys
import time
import os
import shutil
import subprocess
import threading

from instagram_private_api_extensions import live, replay
from instagram_private_api import ClientError

from .logger import log, seperator
from .comments import CommentsDownloader


def main(instagram_api_arg, record_arg, settings_arg):
	global instagram_api
	global user_to_record
	global broadcast
	global mpd_url
	global settings
	settings = settings_arg
	instagram_api = instagram_api_arg
	user_to_record = record_arg
	get_user_info(user_to_record)



def run_script(file):
	try:
		FNULL = open(os.devnull, 'w')
		if sys.version.split(' ')[0].startswith('2'):
			subprocess.call(["python", file], stdout=FNULL, stderr=subprocess.STDOUT)
		else:
			subprocess.call(["python3", file], stdout=FNULL, stderr=subprocess.STDOUT)
	except OSError as e:
		pass



def get_stream_duration(compare_time, broadcast=None):
	try:
		if broadcast:
			record_time = int(time.time()) - int(compare_time)
			stream_time = int(time.time()) - int(broadcast['published_time'])
			stream_started_mins, stream_started_secs = divmod(stream_time - record_time, 60)
		else:
			stream_started_mins, stream_started_secs = divmod((int(time.time()) - int(compare_time)), 60)
		stream_duration_str = '%d minutes' % stream_started_mins
		if stream_started_secs:
			stream_duration_str += ' and %d seconds' % stream_started_secs
		return stream_duration_str
	except:
		return "not available"



def download_livestream(broadcast):
	try:
		def print_status(sep=True):
			heartbeat_info = instagram_api.broadcast_heartbeat_and_viewercount(broadcast['id'])
			viewers = broadcast.get('viewer_count', 0)
			if sep:
				seperator("GREEN")
			log('[I] Viewers     : {:s} watching'.format(str(int(viewers))), "GREEN")
			log('[I] Airing time : {:s}'.format(get_stream_duration(broadcast['published_time'])), "GREEN")
			log('[I] Status      : {:s}'.format(heartbeat_info['broadcast_status'].title()), "GREEN")
			return heartbeat_info['broadcast_status'] not in ['active', 'interrupted']

		mpd_url = (broadcast.get('dash_manifest')
				 or broadcast.get('dash_abr_playback_url')
				 or broadcast['dash_playback_url'])

		output_dir = settings.save_path + '{}_{}_{}_{}_live_downloads'.format(settings.current_date, user_to_record, broadcast['id'], settings.current_time)

		broadcast_downloader = live.Downloader(
			mpd=mpd_url,
			output_dir=output_dir,
			user_agent=instagram_api.user_agent,
			max_connection_error_retry=3,
			duplicate_etag_retry=30,
			callback_check=print_status,
			mpd_download_timeout=3,
			download_timeout=3)
	except Exception as e:
		log('[E] Could not start downloading livestream: {:s}'.format(str(e)), "RED")
		seperator("GREEN")
		sys.exit(1)
	try:
		log('[I] Livestream found, beginning download...', "GREEN")
		if (broadcast['broadcast_owner']['username'] != user_to_record):
			log('[I] This livestream is a dual-live, the owner is "{}".'.format(broadcast['broadcast_owner']['username']), "YELLOW")
		seperator("GREEN")
		log('[I] Username    : {:s}'.format(user_to_record), "GREEN")
		print_status(False)
		log('[I] MPD URL     : {:s}'.format(mpd_url), "GREEN")
		seperator("GREEN")
		log('[I] Downloading livestream... press [CTRL+C] to abort.', "GREEN")

		if (settings.run_at_start is not "None"):
			try:
				thread = threading.Thread(target=run_script, args=(settings.run_at_start,))
				thread.daemon = True
				thread.start()
				log("[I] Executed file to run at start.", "GREEN")
			except Exception as e:
				log('[W] Could not run file: {:s}'.format(str(e)), "YELLOW")


		comment_thread_worker = None
		if settings.save_comments.title() == "True":
			try:
				comments_json_file = settings.save_path + '{}_{}_{}_{}_live_comments.json'.format(settings.current_date, user_to_record, broadcast['id'], settings.current_time)
				comment_thread_worker = threading.Thread(target=get_live_comments, args=(instagram_api, broadcast, comments_json_file, broadcast_downloader,))
				comment_thread_worker.start()
			except Exception as e:
				log('[E] An error occurred while checking comments: {:s}'.format(str(e)), "RED")
		broadcast_downloader.run()
		seperator("GREEN")
		log('[I] The livestream has ended.\n[I] Time recorded     : {}\n[I] Stream duration   : {}\n[I] Missing (approx.) : {}'.format(get_stream_duration(int(settings.current_time)), get_stream_duration(broadcast['published_time']), get_stream_duration(int(settings.current_time), broadcast)), "YELLOW")
		seperator("GREEN")
		stitch_video(broadcast_downloader, broadcast, comment_thread_worker)
	except KeyboardInterrupt:
		seperator("GREEN")
		log('[I] The download has been aborted by the user.\n[I] Time recorded     : {}\n[I] Stream duration   : {}\n[I] Missing (approx.) : {}'.format(get_stream_duration(int(settings.current_time)), get_stream_duration(broadcast['published_time']), get_stream_duration(int(settings.current_time), broadcast)), "YELLOW")
		seperator("GREEN")
		if not broadcast_downloader.is_aborted:
			broadcast_downloader.stop()
			stitch_video(broadcast_downloader, broadcast, comment_thread_worker)



def stitch_video(broadcast_downloader, broadcast, comment_thread_worker):
	try:
		if comment_thread_worker and comment_thread_worker.is_alive():
			log("[I] Stopping comment downloading and saving comments (if any)...", "GREEN")
			comment_thread_worker.join()

		if (settings.run_at_finish is not "None"):
			try:
				thread = threading.Thread(target=run_script, args=(settings.run_at_finish,))
				thread.daemon = True
				thread.start()
				log("[I] Executed file to run at finish.", "GREEN")
			except Exception as e:
				log('[W] Could not run file: {:s}'.format(str(e)), "YELLOW")

		log('[I] Stitching downloaded files into video...', "GREEN")
		output_file = settings.save_path + '{}_{}_{}_{}_live.mp4'.format(settings.current_date, user_to_record, broadcast['id'], settings.current_time)
		try:
			if settings.clear_temp_files.title() == "True":
				broadcast_downloader.stitch(output_file, cleartempfiles=True)
			else:
				broadcast_downloader.stitch(output_file, cleartempfiles=False)
			log('[I] Successfully stitched downloaded files into video.', "GREEN")
			seperator("GREEN")
			sys.exit(0)
		except Exception as e:
			log('[E] Could not stitch downloaded files: {:s}'.format(str(e)), "RED")
			seperator("GREEN")
			sys.exit(1)
	except KeyboardInterrupt:
			log('[I] Aborted stitching process, no video was created.', "YELLOW")
			seperator("GREEN")
			sys.exit(0)



def get_user_info(user_to_record):
	try:
		user_res = instagram_api.username_info(user_to_record)
		user_id = user_res['user']['pk']
	except Exception as e:
		log('[E] Could not get information for "{:s}": {:s}'.format(user_to_record, str(e)), "RED")
		seperator("GREEN")
		sys.exit(1)
	except KeyboardInterrupt:
		log('[W] Aborted getting information for "{:s}", exiting...'.format(user_to_record), "YELLOW")
		seperator("GREEN")
		sys.exit(1)
	log('[I] Getting info for "{:s}" successful.'.format(user_to_record), "GREEN")
	get_broadcasts_info(user_id)



def get_broadcasts_info(user_id):
	seperator("GREEN")
	log('[I] Checking for livestreams and replays...', "GREEN")
	broadcasts = instagram_api.user_story_feed(user_id)

	livestream = broadcasts.get('broadcast')
	replays = broadcasts.get('post_live_item', {}).get('broadcasts', [])

	if livestream:
		seperator("GREEN")
		download_livestream(livestream)
	else:
		log('[I] There are no available livestreams.', "YELLOW")
	if settings.save_replays.title() == "True":
		if replays:
			seperator("GREEN")
			download_replays(replays)
		else:
			log('[I] There are no available replays.', "YELLOW")
	else:
		log("[I] Replay saving is disabled either with a flag or in the config file.", "BLUE")
	seperator("GREEN")


def download_replays(broadcasts):
	try:
		log("[I] Downloading replays... press [CTRL+C] to abort.", "GREEN")
		seperator("GREEN")
		for replay_index, broadcast in enumerate(broadcasts):
			exists = False

			if sys.version.split(' ')[0].startswith('2'):
				directories = (os.walk(settings.save_path).next()[1])
			else:
				directories = (os.walk(settings.save_path).__next__()[1])

			for directory in directories:
				if (str(broadcast['id']) in directory) and ("_live_" not in directory):
					log("[W] Already downloaded a replay with ID '{:s}'.".format(str(broadcast['id'])), "YELLOW")
					exists = True
			if not exists:
				current = replay_index + 1
				log("[I] Downloading replay {:s} of {:s} with ID '{:s}'...".format(str(current), str(len(broadcasts)), str(broadcast['id'])), "GREEN")
				current_time = str(int(time.time()))
				output_dir = settings.save_path + '{}_{}_{}_{}_replay_downloads'.format(settings.current_date, user_to_record, broadcast['id'], settings.current_time)
				broadcast_downloader = replay.Downloader(
					mpd=broadcast['dash_manifest'],
					output_dir=output_dir,
					user_agent=instagram_api.user_agent)


				if settings.clear_temp_files.title() == "True":
					replay_saved = broadcast_downloader.download(settings.save_path + '{}_{}_{}_{}_replay.mp4'.format(settings.current_date, user_to_record, broadcast['id'], settings.current_time), cleartempfiles=True)
				else:
					replay_saved = broadcast_downloader.download(settings.save_path + '{}_{}_{}_{}_replay.mp4'.format(settings.current_date, user_to_record, broadcast['id'], settings.current_time), cleartempfiles=False)

				if settings.save_comments.title() == "True":
					log("[I] Checking for available comments to save...", "GREEN")
					comments_json_file = settings.save_path + '{}_{}_{}_{}_replay_comments.json'.format(settings.current_date, user_to_record, broadcast['id'], settings.current_time)
					get_replay_comments(instagram_api, broadcast, comments_json_file, broadcast_downloader)

				if (len(replay_saved) == 1):
					log("[I] Finished downloading replay {:s} of {:s}.".format(str(current), str(len(broadcasts))), "GREEN")
					if (current != len(broadcasts)):
						seperator("GREEN")
				else:
					log("[W] No output video file was made, please merge the files manually if possible.", "YELLOW")
					log("[W] Check if ffmpeg is available by running ffmpeg in your terminal/cmd prompt.", "YELLOW")
					log("", "GREEN")

		seperator("GREEN")
		log("[I] Finished downloading all available replays.", "GREEN")
		seperator("GREEN")
		sys.exit(0)
	except Exception as e:
		log('[E] Could not save replay: {:s}'.format(str(e)), "RED")
		seperator("GREEN")
		sys.exit(1)
	except KeyboardInterrupt:
		seperator("GREEN")
		log('[I] The download has been aborted by the user.', "YELLOW")
		seperator("GREEN")
		try:
			shutil.rmtree(output_dir)
		except Exception as e:
			log("[E] Could not remove temp folder: {:s}".format(str(e)), "RED")
			sys.exit(1)
		sys.exit(0)



def get_replay_comments(instagram_api, broadcast, comments_json_file, broadcast_downloader):
	comments_downloader = CommentsDownloader(
		api=instagram_api, broadcast=broadcast, destination_file=comments_json_file)
	comments_downloader.get_replay()

	try:
		if comments_downloader.comments:
			comments_log_file = comments_json_file.replace('.json', '.log')
			CommentsDownloader.generate_log(
				comments_downloader.comments, broadcast['published_time'], comments_log_file,
				comments_delay=0)
			if len(comments_downloader.comments) == 1:
				log("[I] Successfully saved 1 comment to logfile.", "GREEN")
			else:
				log("[I] Successfully saved {} comments to logfile.".format(len(comments_downloader.comments)), "GREEN")
		else:
			log("[I] There are no available comments to save.", "GREEN")
	except Exception as e:
		log('[E] Could not save comments to logfile: {:s}'.format(str(e)), "RED")



def get_live_comments(instagram_api, broadcast, comments_json_file, broadcast_downloader):
	comments_downloader = CommentsDownloader(
		api=instagram_api, broadcast=broadcast, destination_file=comments_json_file)
	first_comment_created_at = 0
	try:
		while not broadcast_downloader.is_aborted:
			if 'initial_buffered_duration' not in broadcast and broadcast_downloader.initial_buffered_duration:
				broadcast['initial_buffered_duration'] = broadcast_downloader.initial_buffered_duration
				comments_downloader.broadcast = broadcast
			first_comment_created_at = comments_downloader.get_live(first_comment_created_at)
	except ClientError as e:
		if not 'media has been deleted' in e.error_response:
			log("[W] Comment collection ClientError: %d %s" % (e.code, e.error_response), "YELLOW")

	try:
		if comments_downloader.comments:
			comments_downloader.save()
			comments_log_file = comments_json_file.replace('.json', '.log')
			CommentsDownloader.generate_log(
				comments_downloader.comments, settings.current_time, comments_log_file,
				comments_delay=broadcast_downloader.initial_buffered_duration)
			if len(comments_downloader.comments) == 1:
				log("[I] Successfully saved 1 comment to logfile.", "GREEN")
			else:
				log("[I] Successfully saved {} comments to logfile.".format(len(comments_downloader.comments)), "GREEN")
			seperator("GREEN")
		else:
			log("[I] There are no available comments to save.", "GREEN")
			seperator("GREEN")
	except Exception as e:
		log('[E] Could not save comments to logfile: {:s}'.format(str(e)), "RED")