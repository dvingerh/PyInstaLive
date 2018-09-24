import os
import shutil
import subprocess
import sys
import threading
import time
import shlex
import json

from xml.dom.minidom import parse, parseString

from instagram_private_api import ClientConnectionError
from instagram_private_api import ClientError
from instagram_private_api import ClientThrottledError
from instagram_private_api_extensions import live
from instagram_private_api_extensions import replay

from .comments import CommentsDownloader
from .logger import log_seperator, supports_color, log_info_blue, log_info_green, log_warn, log_error, log_whiteline, log_plain



def start_single(instagram_api_arg, download_arg, settings_arg):
	global instagram_api
	global user_to_download
	global broadcast
	global settings
	settings = settings_arg
	instagram_api = instagram_api_arg
	user_to_download = download_arg
	try:
		if not os.path.isfile(os.path.join(settings.save_path, user_to_download + '.lock')):
			open(os.path.join(settings.save_path, user_to_download + '.lock'), 'a').close()
		else:
			log_warn("Lock file is already present for this user, there is probably another download ongoing!")
			log_warn("If this is not the case, manually delete the file '{:s}' and try again.".format(user_to_download + '.lock'))
			log_seperator()
			sys.exit(1)
	except Exception:
		log_warn("Lock file could not be created. Downloads started from -df might cause problems!")
	get_user_info(user_to_download)

def start_multiple(instagram_api_arg, settings_arg, proc_arg):
	try:
		log_info_green("Checking following users for any livestreams or replays...")
		broadcast_f_list = instagram_api_arg.reels_tray()
		usernames_available = []
		if broadcast_f_list['broadcasts']:
			for broadcast_f in broadcast_f_list['broadcasts']:
				username = broadcast_f['broadcast_owner']['username']
				if username not in usernames_available:
					usernames_available.append(username)

		if broadcast_f_list.get('post_live', {}).get('post_live_items', []):
			for broadcast_r in broadcast_f_list.get('post_live', {}).get('post_live_items', []):
				for broadcast_f in broadcast_r.get("broadcasts", []):
					username = broadcast_f['broadcast_owner']['username']
					if username not in usernames_available:
						usernames_available.append(username)
		log_seperator()
		if usernames_available:
			log_info_green("The following users have available livestreams or replays:")
			log_info_green(', '.join(usernames_available))
			log_seperator()
			for user in usernames_available:
				try:
					if os.path.isfile(os.path.join(settings_arg.save_path, user + '.lock')):
						log_warn("Lock file is already present for '{:s}', there is probably another download ongoing!".format(user))
						log_warn("If this is not the case, manually delete the file '{:s}' and try again.".format(user + '.lock'))
					else:
						log_info_green("Launching daemon process for '{:s}'...".format(user))
						start_result = run_command("{:s} -d {:s}".format(proc_arg, user))
						if start_result:
							log_info_green("Could not start processs: {:s}".format(str(start_result)))
						else:
							log_info_green("Process started successfully.")
					log_seperator()	
					time.sleep(2)
				except Exception as e:
					log_error("Could not start processs: {:s}".format(str(e)))
				except KeyboardInterrupt:
					log_info_blue('The process launching has been aborted by the user.')
					log_seperator()				
					sys.exit(0)
		else:
			log_info_green("There are currently no available livestreams or replays.")
			log_seperator()
			sys.exit(0)
	except Exception as e:
		log_error("Could not finish checking following users: {:s}".format(str(e)))
		sys.exit(1)
	except KeyboardInterrupt:
		log_seperator()
		log_info_blue('The checking process has been aborted by the user.')
		log_seperator()
		sys.exit(0)



def run_command(command):
	try:
		FNULL = open(os.devnull, 'w')
		subprocess.Popen(shlex.split(command), stdout=FNULL, stderr=subprocess.STDOUT)
		return False
	except Exception as e:
		return str(e)



def get_stream_duration(compare_time, broadcast=None):
	try:
		had_wrong_time = False
		if broadcast:
			if (int(time.time()) < int(compare_time)):
				had_wrong_time = True				
				corrected_compare_time = int(compare_time) - 5
				download_time = int(time.time()) - int(corrected_compare_time)
			else:
				download_time = int(time.time()) - int(compare_time)
			stream_time = int(time.time()) - int(broadcast.get('published_time'))
			stream_started_mins, stream_started_secs = divmod(stream_time - download_time, 60)
		else:
			if (int(time.time()) < int(compare_time)):	
				had_wrong_time = True			
				corrected_compare_time = int(compare_time) - 5
				stream_started_mins, stream_started_secs = divmod((int(time.time()) - int(corrected_compare_time)), 60)
			else:
				stream_started_mins, stream_started_secs = divmod((int(time.time()) - int(compare_time)), 60)
		stream_duration_str = '%d minutes' % stream_started_mins
		if stream_started_secs:
			stream_duration_str += ' and %d seconds' % stream_started_secs
		if had_wrong_time:
			return "{:s} (corrected)".format(stream_duration_str)
		else:
			return stream_duration_str
	except Exception as e:
		return "Not available"



def download_livestream(broadcast):
	try:
		def print_status(sep=True):
			heartbeat_info = instagram_api.broadcast_heartbeat_and_viewercount(broadcast.get('id'))
			viewers = broadcast.get('viewer_count', 0)
			if sep:
				log_seperator()
			log_info_green('Viewers     : {:s} watching'.format(str(int(viewers))))
			log_info_green('Airing time : {:s}'.format(get_stream_duration(broadcast.get('published_time'))))
			log_info_green('Status      : {:s}'.format(heartbeat_info.get('broadcast_status').title()))
			return heartbeat_info.get('broadcast_status') not in ['active', 'interrupted']

		mpd_url = (broadcast.get('dash_manifest')
				 or broadcast.get('dash_abr_playback_url')
				 or broadcast.get('dash_playback_url'))

		output_dir = '{}{}_{}_{}_{}_live_downloads'.format(settings.save_path, settings.current_date, user_to_download, broadcast.get('id'), settings.current_time)

		broadcast_downloader = live.Downloader(
			mpd=mpd_url,
			output_dir=output_dir,
			user_agent=instagram_api.user_agent,
			max_connection_error_retry=3,
			duplicate_etag_retry=30,
			callback_check=print_status,
			mpd_download_timeout=3,
			download_timeout=3,
			ffmpeg_binary=settings.ffmpeg_path)
	except Exception as e:
		log_error('Could not start downloading livestream: {:s}'.format(str(e)))
		log_seperator()
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass
		sys.exit(1)
	try:
		log_info_green('Livestream found, beginning download...')
		broadcast_owner = broadcast.get('broadcast_owner', {}).get('username')
		try:
			broadcast_guest = broadcast.get('cobroadcasters', {})[0].get('username')
		except Exception:
			broadcast_guest = None
		if (broadcast_owner != user_to_download):
			log_info_blue('This livestream is a dual-live, the owner is "{}".'.format(broadcast_owner))
			broadcast_guest = None
		if broadcast_guest:
			log_info_blue('This livestream is a dual-live, the current guest is "{}".'.format(broadcast_guest))
		log_seperator()
		log_info_green('Username    : {:s}'.format(user_to_download))
		print_status(False)
		log_info_green('MPD URL     : {:s}'.format(mpd_url))
		log_seperator()
		open(os.path.join(output_dir, 'folder.lock'), 'a').close()
		log_info_green('Downloading livestream... press [CTRL+C] to abort.')

		if (settings.run_at_start is not "None"):
			try:
				thread = threading.Thread(target=run_command, args=(settings.run_at_start,))
				thread.daemon = True
				thread.start()
				log_info_green("Command executed: \033[94m{:s}".format(settings.run_at_start))
			except Exception as e:
				log_warn('Could not execute command: {:s}'.format(str(e)))


		comment_thread_worker = None
		if settings.save_comments.title() == "True":
			try:
				comments_json_file = os.path.join(output_dir, '{}_{}_{}_{}_live_comments.json'.format(settings.current_date, user_to_download, broadcast.get('id'), settings.current_time))
				comment_thread_worker = threading.Thread(target=get_live_comments, args=(instagram_api, broadcast, comments_json_file, broadcast_downloader,))
				comment_thread_worker.start()
			except Exception as e:
				log_error('An error occurred while downloading comments: {:s}'.format(str(e)))
		broadcast_downloader.run()
		log_seperator()
		log_info_green('Download duration : {}'.format(get_stream_duration(int(settings.current_time))))
		log_info_green('Stream duration   : {}'.format(get_stream_duration(broadcast.get('published_time'))))
		log_info_green('Missing (approx.) : {}'.format(get_stream_duration(int(settings.current_time), broadcast)))
		log_seperator()
		stitch_video(broadcast_downloader, broadcast, comment_thread_worker)
	except KeyboardInterrupt:
		log_seperator()
		log_info_blue('The download has been aborted by the user.')
		log_seperator()
		log_info_green('Download duration : {}'.format(get_stream_duration(int(settings.current_time))))
		log_info_green('Stream duration   : {}'.format(get_stream_duration(broadcast.get('published_time'))))
		log_info_green('Missing (approx.) : {}'.format(get_stream_duration(int(settings.current_time), broadcast)))
		log_seperator()
		if not broadcast_downloader.is_aborted:
			broadcast_downloader.stop()
			stitch_video(broadcast_downloader, broadcast, comment_thread_worker)
	except Exception as e:
		log_error("Could not download livestream: {:s}".format(str(e)))
		try:
			os.remove(os.path.join(output_dir, 'folder.lock'))
		except Exception:
			pass
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass


def stitch_video(broadcast_downloader, broadcast, comment_thread_worker):
	try:
		live_mp4_file = '{}{}_{}_{}_{}_live.mp4'.format(settings.save_path, settings.current_date, user_to_download, broadcast.get('id'), settings.current_time)
		live_folder_path = "{:s}_downloads".format(live_mp4_file.split('.mp4')[0])

		if comment_thread_worker and comment_thread_worker.is_alive():
			log_info_green("Waiting for comment downloader to end cycle...")
			comment_thread_worker.join()

		if (settings.run_at_finish is not "None"):
			try:
				thread = threading.Thread(target=run_command, args=(settings.run_at_finish,))
				thread.daemon = True
				thread.start()
				log_info_green("Command executed: \033[94m{:s}".format(settings.run_at_finish))
			except Exception as e:
				log_warn('Could not execute command: {:s}'.format(str(e)))

		log_info_green('Stitching downloaded files into video...')		
		try:
			if settings.clear_temp_files.title() == "True":
				broadcast_downloader.stitch(live_mp4_file, cleartempfiles=True)
			else:
				broadcast_downloader.stitch(live_mp4_file, cleartempfiles=False)
			log_info_green('Successfully stitched downloaded files into video.')
			try:
				os.remove(os.path.join(live_folder_path, 'folder.lock'))
			except Exception:
				pass
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			if settings.clear_temp_files.title() == "True":
				try:
					shutil.rmtree(live_folder_path)
				except Exception as e:
					log_error("Could not remove temp folder: {:s}".format(str(e)))
			log_seperator()
			sys.exit(0)
		except ValueError as e:
			log_error('Could not stitch downloaded files: {:s}'.format(str(e)))
			log_error('Likely the download duration was too short and no temp files were saved.')
			log_seperator()
			try:
				os.remove(os.path.join(live_folder_path, 'folder.lock'))
			except Exception:
				pass
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			sys.exit(1)
		except Exception as e:
			log_error('Could not stitch downloaded files: {:s}'.format(str(e)))
			log_seperator()
			try:
				os.remove(os.path.join(live_folder_path, 'folder.lock'))
			except Exception:
				pass
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			sys.exit(1)
	except KeyboardInterrupt:
			log_info_blue('Aborted stitching process, no video was created.')
			log_seperator()
			try:
				os.remove(os.path.join(live_folder_path, 'folder.lock'))
			except Exception:
				pass
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			sys.exit(0)



def get_user_info(user_to_download):
	is_user_id = False
	if ((type(eval(user_to_download)) == int)):
		is_user_id = True
		user_id = user_to_download
	else:
		try:
			user_res = instagram_api.username_info(user_to_download)
			user_id = user_res.get('user', {}).get('pk')
		except ClientConnectionError as cce:
			log_error('Could not get user info for "{:s}": {:d} {:s}'.format(user_to_download, cce.code, str(cce)))
			if "getaddrinfo failed" in str(cce):
				log_error('Could not resolve host, check your internet connection.')
			if "timed out" in str(cce):
				log_error('The connection timed out, check your internet connection.')
			log_seperator()
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			sys.exit(1)
		except ClientThrottledError as cte:
			log_error('Could not get user info for "{:s}": {:d} {:s}.'.format(user_to_download, cte.code, str(cte)))
			log_error('You are making too many requests at this time.')
			log_seperator()
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			sys.exit(1)
		except ClientError as ce:
			log_error('Could not get user info for "{:s}": {:d} {:s}'.format(user_to_download, ce.code, str(ce)))
			if ("Not Found") in str(ce):
				log_error('The specified user does not exist.')
			log_seperator()
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			sys.exit(1)
		except Exception as e:
			log_error('Could not get user info for "{:s}": {:s}'.format(user_to_download, str(e)))
			log_seperator()
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			sys.exit(1)
		except KeyboardInterrupt:
			log_info_blue('Aborted getting user info for "{:s}", exiting...'.format(user_to_download))
			log_seperator()
			try:
				os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
			except Exception:
				pass
			sys.exit(0)
	if is_user_id:
		log_info_green('Getting info for "{:s}" successful. (assumed user Id as input)'.format(user_to_download))
	else:
		log_info_green('Getting info for "{:s}" successful.'.format(user_to_download))
	get_broadcasts_info(user_id)



def get_broadcasts_info(user_id):
	try:
		log_seperator()
		log_info_green('Checking for livestreams and replays...')
		log_seperator()
		broadcasts = instagram_api.user_story_feed(user_id)

		livestream = broadcasts.get('broadcast')
		replays = broadcasts.get('post_live_item', {}).get('broadcasts', [])

		if settings.save_lives.title() == "True":
			if livestream:
				download_livestream(livestream)
			else:
				log_info_green('There are no available livestreams.')
		else:
			log_info_blue("Livestream saving is disabled either with an argument or in the config file.")
			

		if settings.save_replays.title() == "True":
			if replays:
				log_seperator()
				log_info_green('Replays found, beginning download...')
				log_seperator()
				download_replays(replays)
			else:
				log_info_green('There are no available replays.')
		else:
			log_seperator()
			log_info_blue("Replay saving is disabled either with an argument or in the config file.")

		log_seperator()
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass
	except Exception as e:
		log_error('Could not finish checking: {:s}'.format(str(e)))
		if "timed out" in str(e):
			log_error('The connection timed out, check your internet connection.')
		log_seperator()
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass
		sys.exit(1)
	except KeyboardInterrupt:
		log_info_blue('Aborted checking for livestreams and replays, exiting...'.format(user_to_download))
		log_seperator()
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass
		sys.exit(1)
	except ClientThrottledError as cte:
		log_error('Could not check because you are making too many requests at this time.')
		log_seperator()
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass
		sys.exit(1)

def download_replays(broadcasts):
	try:
		try:
			log_info_green('Amount of replays    : {:s}'.format(str(len(broadcasts))))
			for replay_index, broadcast in enumerate(broadcasts):
				bc_dash_manifest = parseString(broadcast.get('dash_manifest')).getElementsByTagName('Period')
				bc_duration_raw = bc_dash_manifest[0].getAttribute("duration")	
				bc_hours = (bc_duration_raw.split("PT"))[1].split("H")[0]
				bc_minutes = (bc_duration_raw.split("H"))[1].split("M")[0]
				bc_seconds = ((bc_duration_raw.split("M"))[1].split("S")[0]).split('.')[0]
				log_info_green('Replay {:s} duration    : {:s} minutes and {:s} seconds'.format(str(replay_index + 1), bc_minutes, bc_seconds))
		except Exception as e:
			log_warn("An error occurred while getting replay duration information: {:s}".format(str(e)))
		log_seperator()
		log_info_green("Downloading replays... press [CTRL+C] to abort.")
		log_seperator()
		for replay_index, broadcast in enumerate(broadcasts):
			exists = False

			if sys.version.split(' ')[0].startswith('2'):
				directories = (os.walk(settings.save_path).next()[1])
			else:
				directories = (os.walk(settings.save_path).__next__()[1])

			for directory in directories:
				if (str(broadcast.get('id')) in directory) and ("_live_" not in directory):
					log_info_blue("Already downloaded a replay with ID '{:s}'.".format(str(broadcast.get('id'))))
					exists = True
			if not exists:
				current = replay_index + 1
				log_info_green("Downloading replay {:s} of {:s} with ID '{:s}'...".format(str(current), str(len(broadcasts)), str(broadcast.get('id'))))
				current_time = str(int(time.time()))
				output_dir = '{}{}_{}_{}_{}_replay_downloads'.format(settings.save_path, settings.current_date, user_to_download, broadcast.get('id'), settings.current_time)
				broadcast_downloader = replay.Downloader(
					mpd=broadcast.get('dash_manifest'),
					output_dir=output_dir,
					user_agent=instagram_api.user_agent,
					ffmpeg_binary=settings.ffmpeg_path)
				open(os.path.join(output_dir, 'folder.lock'), 'a').close()
				replay_mp4_file = '{}{}_{}_{}_{}_replay.mp4'.format(settings.save_path, settings.current_date, user_to_download, broadcast.get('id'), settings.current_time)
				replay_json_file = os.path.join(output_dir, '{}_{}_{}_{}_replay_comments.json'.format(settings.current_date, user_to_download, broadcast.get('id'), settings.current_time))

				if settings.clear_temp_files.title() == "True":
					replay_saved = broadcast_downloader.download(replay_mp4_file, cleartempfiles=True)
				else:
					replay_saved = broadcast_downloader.download(replay_mp4_file, cleartempfiles=False)

				if settings.save_comments.title() == "True":
					log_info_green("Downloading replay comments...")
					try:
						get_replay_comments(instagram_api, broadcast, replay_json_file, broadcast_downloader)
					except Exception as e:
						log_error('An error occurred while downloading comments: {:s}'.format(str(e)))

				if (len(replay_saved) == 1):
					log_info_green("Finished downloading replay {:s} of {:s}.".format(str(current), str(len(broadcasts))))
					try:
						os.remove(os.path.join(output_dir, 'folder.lock'))
					except Exception:
						pass

					if (current != len(broadcasts)):
						log_seperator()

				else:
					log_warn("No output video file was made, please merge the files manually if possible.")
					log_warn("Check if ffmpeg is available by running ffmpeg in your terminal/cmd prompt.")
					log_whiteline()

		log_seperator()
		log_info_green("Finished downloading all available replays.")
		log_seperator()
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass
		sys.exit(0)
	except Exception as e:
		log_error('Could not save replay: {:s}'.format(str(e)))
		log_seperator()
		try:
			os.remove(os.path.join(output_dir, 'folder.lock'))
		except Exception:
			pass
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass
		sys.exit(1)
	except KeyboardInterrupt:
		log_seperator()
		log_info_blue('The download has been aborted by the user, exiting...')
		log_seperator()
		try:
			shutil.rmtree(output_dir)
		except Exception as e:
			log_error("Could not remove temp folder: {:s}".format(str(e)))
			sys.exit(1)
		try:
			os.remove(os.path.join(settings.save_path, user_to_download + '.lock'))
		except Exception:
			pass
		sys.exit(0)



def get_replay_comments(instagram_api, broadcast, comments_json_file, broadcast_downloader):
	try:
		comments_downloader = CommentsDownloader(
			api=instagram_api, broadcast=broadcast, destination_file=comments_json_file)
		comments_downloader.get_replay()

		try:
			if comments_downloader.comments:
				comments_log_file = comments_json_file.replace('.json', '.log')
				comment_errors, total_comments = CommentsDownloader.generate_log(
					comments_downloader.comments, broadcast.get('published_time'), comments_log_file,
					comments_delay=0)
				if total_comments == 1:
					log_info_green("Successfully saved 1 comment to logfile.")
					log_seperator()
					return True
				else:
					if comment_errors:
						log_warn("Successfully saved {:s} comments to logfile but {:s} comments are (partially) missing.".format(str(total_comments), str(comment_errors)))
					else:
						log_info_green("Successfully saved {:s} comments to logfile.".format(str(total_comments)))
					log_seperator()
					return True
			else:
				log_info_green("There are no available comments to save.")
				return False
		except Exception as e:
			log_error('Could not save comments to logfile: {:s}'.format(str(e)))
			return False
	except KeyboardInterrupt as e:
		log_info_blue("Downloading replay comments has been aborted.")
		return False



def get_live_comments(instagram_api, broadcast, comments_json_file, broadcast_downloader):
	try:
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
				log_warn("Comment collection ClientError: %d %s" % (e.code, e.error_response))

		try:
			if comments_downloader.comments:
				comments_downloader.save()
				comments_log_file = comments_json_file.replace('.json', '.log')
				comment_errors, total_comments = CommentsDownloader.generate_log(
					comments_downloader.comments, settings.current_time, comments_log_file,
					comments_delay=broadcast_downloader.initial_buffered_duration)
				if len(comments_downloader.comments) == 1:
					log_info_green("Successfully saved 1 comment to logfile.")
					log_seperator()
					return True
				else:
					if comment_errors:
						log_warn("Successfully saved {:s} comments to logfile but {:s} comments are (partially) missing.".format(str(total_comments), str(comment_errors)))
					else:
						log_info_green("Successfully saved {:s} comments to logfile.".format(str(total_comments)))
					log_seperator()
					return True
			else:
				log_info_green("There are no available comments to save.")
				return False
				log_seperator()
		except Exception as e:
			log_error('Could not save comments to logfile: {:s}'.format(str(e)))
			return False
	except KeyboardInterrupt as e:
		log_info_blue("Downloading livestream comments has been aborted.")
		return False