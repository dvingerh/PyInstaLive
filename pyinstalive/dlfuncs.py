import os
import shutil
import json
import threading
import time

from xml.dom.minidom import parseString

from instagram_private_api import ClientConnectionError
from instagram_private_api import ClientError
from instagram_private_api import ClientThrottledError
from instagram_private_api_extensions import live
from instagram_private_api_extensions import replay

try:
    import logger
    import helpers
    import pil
    import dlfuncs
    import assembler
    from constants import Constants
    from comments import CommentsDownloader
except ImportError:
    from . import logger
    from . import helpers
    from . import pil
    from . import assembler
    from . import dlfuncs
    from .constants import Constants
    from .comments import CommentsDownloader


def get_stream_duration(duration_type):
    try:
        # For some reason the published_time is roughly 40 seconds behind real world time
        if duration_type == 0: # Airtime duration
            stream_started_mins, stream_started_secs = divmod((int(time.time()) - pil.livestream_obj.get("published_time") + 40), 60)
        if duration_type == 1: # Download duration
            stream_started_mins, stream_started_secs = divmod((int(time.time()) - int(pil.epochtime)), 60)
        if duration_type == 2: # Missing duration
            if (int(pil.epochtime) - pil.livestream_obj.get("published_time") + 40) <= 0:
                stream_started_mins, stream_started_secs = 0, 0 # Download started 'earlier' than actual broadcast, assume started at the same time instead
            else:
                stream_started_mins, stream_started_secs = divmod((int(pil.epochtime) - pil.livestream_obj.get("published_time") + 40), 60)

        if stream_started_mins < 0:
            stream_started_mins = 0
        if stream_started_secs < 0:
            stream_started_secs = 0
        stream_duration_str = '%d minutes' % stream_started_mins
        if stream_started_secs:
            stream_duration_str += ' and %d seconds' % stream_started_secs
        return stream_duration_str
    except Exception as e:
        return "Not available"


def get_user_id():
    is_user_id = False
    user_id = None
    try:
        user_id = int(pil.dl_user)
        is_user_id = True
    except ValueError:
        try:
            user_res = pil.ig_api.username_info(pil.dl_user)
            user_id = user_res.get('user', {}).get('pk')
        except ClientConnectionError as cce:
            logger.error(
                "Could not get user info for '{:s}': {:d} {:s}".format(pil.dl_user, cce.code, str(cce)))
            if "getaddrinfo failed" in str(cce):
                logger.error('Could not resolve host, check your internet connection.')
            if "timed out" in str(cce):
                logger.error('The connection timed out, check your internet connection.')
        except ClientThrottledError as cte:
            logger.error(
                "Could not get user info for '{:s}': {:d} {:s}".format(pil.dl_user, cte.code, str(cte)))
        except ClientError as ce:
            logger.error(
                "Could not get user info for '{:s}': {:d} {:s}".format(pil.dl_user, ce.code, str(ce)))
            if "Not Found" in str(ce):
                logger.error('The specified user does not exist.')
        except Exception as e:
            logger.error("Could not get user info for '{:s}': {:s}".format(pil.dl_user, str(e)))
        except KeyboardInterrupt:
            logger.binfo("Aborted getting user info for '{:s}', exiting.".format(pil.dl_user))
    if user_id and is_user_id:
        logger.info("Getting info for '{:s}' successful. Assuming input is an user Id.".format(pil.dl_user))
        logger.separator()
        return user_id
    elif user_id:
        logger.info("Getting info for '{:s}' successful.".format(pil.dl_user))
        logger.separator()
        return user_id
    else:
        return None


def get_broadcasts_info():
    try:
        user_id = get_user_id()
        if user_id:
            broadcasts = pil.ig_api.user_story_feed(user_id)
            pil.livestream_obj = broadcasts.get('broadcast')
            pil.replays_obj = broadcasts.get('post_live_item', {}).get('broadcasts', [])
            return True
        else:
            return False
    except Exception as e:
        logger.error('Could not finish checking: {:s}'.format(str(e)))
        if "timed out" in str(e):
            logger.error('The connection timed out, check your internet connection.')
        logger.separator()
        return False
    except KeyboardInterrupt:
        logger.binfo('Aborted checking for livestreams and replays, exiting.'.format(pil.dl_user))
        logger.separator()
        return False
    except ClientThrottledError as cte:
        logger.error('Could not check because you are making too many requests at this time.')
        logger.separator()
        return False


def merge_segments():
    try:
        if pil.run_at_finish:
            try:
                thread = threading.Thread(target=helpers.run_command, args=(pil.run_at_finish,))
                thread.daemon = True
                thread.start()
                logger.binfo("Launched finish command: {:s}".format(pil.run_at_finish))
            except Exception as e:
                logger.warn('Could not execute command: {:s}'.format(str(e)))

        live_mp4_file = '{}{}_{}_{}_live.mp4'.format(pil.dl_path, pil.datetime_compat, pil.dl_user,
                                                     pil.livestream_obj.get('id'))

        live_segments_path = os.path.normpath(pil.broadcast_downloader.output_dir)

        if pil.segments_json_thread_worker and pil.segments_json_thread_worker.is_alive():
            pil.segments_json_thread_worker.join()

        if pil.comment_thread_worker and pil.comment_thread_worker.is_alive():
            logger.info("Waiting for comment downloader to finish.")
            pil.comment_thread_worker.join()
        logger.info('Merging downloaded files into video.')
        try:
            pil.broadcast_downloader.stitch(live_mp4_file, cleartempfiles=pil.clear_temp_files)
            logger.info('Successfully merged downloaded files into video.')
            helpers.remove_lock()
        except ValueError as e:
            logger.separator()
            logger.error('Could not merge downloaded files: {:s}'.format(str(e)))
            if os.listdir(live_segments_path):
                logger.separator()
                logger.binfo("Segment directory is not empty. Trying to merge again.")
                logger.separator()
                pil.assemble_arg = live_mp4_file.replace(".mp4", "_downloads.json")
                assembler.assemble(user_called=False)
            else:
                logger.separator()
                logger.error("Segment directory is empty. There is nothing to merge.")
                logger.separator()
            helpers.remove_lock()
        except Exception as e:
            logger.error('Could not merge downloaded files: {:s}'.format(str(e)))
            helpers.remove_lock()
    except KeyboardInterrupt:
        logger.binfo('Aborted merging process, no video was created.')
        helpers.remove_lock()


def download_livestream():
    try:
        def print_status(sep=True):
            heartbeat_info = pil.ig_api.broadcast_heartbeat_and_viewercount(pil.livestream_obj.get('id'))
            viewers = pil.livestream_obj.get('viewer_count', 0)
            if sep:
                logger.separator()
            else:
                logger.info('Username    : {:s}'.format(pil.dl_user))
            logger.info('Viewers     : {:s} watching'.format(str(int(viewers))))
            logger.info('Airing time : {:s}'.format(get_stream_duration(0)))
            logger.info('Status      : {:s}'.format(heartbeat_info.get('broadcast_status').title()))
            return heartbeat_info.get('broadcast_status') not in ['active', 'interrupted']

        mpd_url = (pil.livestream_obj.get('dash_manifest')
                   or pil.livestream_obj.get('dash_abr_playback_url')
                   or pil.livestream_obj.get('dash_playback_url'))

        pil.live_folder_path = '{}{}_{}_{}_live_downloads'.format(pil.dl_path, pil.datetime_compat,
                                                                  pil.dl_user, pil.livestream_obj.get('id'))
        pil.broadcast_downloader = live.Downloader(
            mpd=mpd_url,
            output_dir=pil.live_folder_path,
            user_agent=pil.ig_api.user_agent,
            max_connection_error_retry=3,
            duplicate_etag_retry=30,
            callback_check=print_status,
            mpd_download_timeout=3,
            download_timeout=3,
            ffmpeg_binary=pil.ffmpeg_path)
    except Exception as e:
        logger.error('Could not start downloading livestream: {:s}'.format(str(e)))
        logger.separator()
        helpers.remove_lock()
    try:
        broadcast_owner = pil.livestream_obj.get('broadcast_owner', {}).get('username')
        try:
            broadcast_guest = pil.livestream_obj.get('cobroadcasters', {})[0].get('username')
        except Exception:
            broadcast_guest = None
        if broadcast_owner != pil.dl_user:
            logger.binfo('This livestream is a dual-live, the owner is "{}".'.format(broadcast_owner))
            broadcast_guest = None
        if broadcast_guest:
            logger.binfo('This livestream is a dual-live, the current guest is "{}".'.format(broadcast_guest))
            pil.has_guest = broadcast_guest
        logger.separator()
        print_status(False)
        logger.separator()
        helpers.create_lock_folder()
        pil.segments_json_thread_worker = threading.Thread(target=helpers.generate_json_segments)
        pil.segments_json_thread_worker.start()
        logger.info('Downloading livestream, press [CTRL+C] to abort.')

        if pil.run_at_start:
            try:
                thread = threading.Thread(target=helpers.run_command, args=(pil.run_at_start,))
                thread.daemon = True
                thread.start()
                logger.binfo("Launched start command: {:s}".format(pil.run_at_start))
            except Exception as e:
                logger.warn('Could not launch command: {:s}'.format(str(e)))

        if pil.dl_comments:
            try:
                comments_json_file = '{}{}_{}_{}_live_comments.json'.format(pil.dl_path, pil.datetime_compat,
                                                                            pil.dl_user, pil.livestream_obj.get('id'))
                pil.comment_thread_worker = threading.Thread(target=get_live_comments, args=(comments_json_file,))
                pil.comment_thread_worker.start()
            except Exception as e:
                logger.error('An error occurred while downloading comments: {:s}'.format(str(e)))
        pil.broadcast_downloader.run()
        logger.separator()
        logger.info("The livestream has been ended by the user.")
        logger.separator()
        logger.info('Airtime duration  : {}'.format(get_stream_duration(0)))
        logger.info('Download duration : {}'.format(get_stream_duration(1)))
        logger.info('Missing (approx.) : {}'.format(get_stream_duration(2)))
        logger.separator()
        merge_segments()
    except KeyboardInterrupt:
        logger.separator()
        logger.binfo('The download has been aborted.')
        logger.separator()
        logger.info('Airtime duration  : {}'.format(get_stream_duration(0)))
        logger.info('Download duration : {}'.format(get_stream_duration(1)))
        logger.info('Missing (approx.) : {}'.format(get_stream_duration(2)))
        logger.separator()
        if not pil.broadcast_downloader.is_aborted:
            pil.broadcast_downloader.stop()
            merge_segments()


def download_replays():
    try:
        try:
            logger.info('Amount of replays    : {:s}'.format(str(len(pil.replays_obj))))
            for replay_index, replay_obj in enumerate(pil.replays_obj):
                bc_dash_manifest = parseString(replay_obj.get('dash_manifest')).getElementsByTagName('Period')
                bc_duration_raw = bc_dash_manifest[0].getAttribute("duration")
                bc_minutes = (bc_duration_raw.split("H"))[1].split("M")[0]
                bc_seconds = ((bc_duration_raw.split("M"))[1].split("S")[0]).split('.')[0]
                logger.info(
                    'Replay {:s} duration    : {:s} minutes and {:s} seconds'.format(str(replay_index + 1), bc_minutes,
                                                                                     bc_seconds))
        except Exception as e:
            logger.warn("An error occurred while getting replay duration information: {:s}".format(str(e)))
        logger.separator()
        logger.info("Downloading replays, press [CTRL+C] to abort.")
        logger.separator()
        for replay_index, replay_obj in enumerate(pil.replays_obj):
            exists = False
            pil.livestream_obj = replay_obj
            if Constants.PYTHON_VER[0][0] == '2':
                directories = (os.walk(pil.dl_path).next()[1])
            else:
                directories = (os.walk(pil.dl_path).__next__()[1])

            for directory in directories:
                if (str(replay_obj.get('id')) in directory) and ("_live_" not in directory):
                    logger.binfo("Already downloaded a replay with ID '{:s}'.".format(str(replay_obj.get('id'))))
                    exists = True
            if not exists:
                current = replay_index + 1
                logger.info(
                    "Downloading replay {:s} of {:s} with ID '{:s}'.".format(str(current), str(len(pil.replays_obj)),
                                                                               str(replay_obj.get('id'))))
                pil.live_folder_path = '{}{}_{}_{}_replay_downloads'.format(pil.dl_path, pil.datetime_compat,
                                                                            pil.dl_user, pil.livestream_obj.get('id'))
                broadcast_downloader = replay.Downloader(
                    mpd=replay_obj.get('dash_manifest'),
                    output_dir=pil.live_folder_path,
                    user_agent=pil.ig_api.user_agent,
                    ffmpeg_binary=pil.ffmpeg_path)
                if pil.use_locks:
                    helpers.create_lock_folder()
                replay_mp4_file = '{}{}_{}_{}_replay.mp4'.format(pil.dl_path, pil.datetime_compat,
                                                                 pil.dl_user, pil.livestream_obj.get('id'))

                comments_json_file = '{}{}_{}_{}_live_comments.json'.format(pil.dl_path, pil.datetime_compat,
                                                                            pil.dl_user, pil.livestream_obj.get('id'))

                pil.comment_thread_worker = threading.Thread(target=get_replay_comments, args=(comments_json_file,))

                broadcast_downloader.download(replay_mp4_file, cleartempfiles=pil.clear_temp_files)

                if pil.dl_comments:
                    logger.info("Downloading replay comments.")
                    try:
                        get_replay_comments(comments_json_file)
                    except Exception as e:
                        logger.error('An error occurred while downloading comments: {:s}'.format(str(e)))

                logger.info("Finished downloading replay {:s} of {:s}.".format(str(current), str(len(pil.replays_obj))))
                try:
                    os.remove(os.path.join(pil.live_folder_path, 'folder.lock'))
                except Exception:
                    pass

                if current != len(pil.replays_obj):
                    logger.separator()

        logger.separator()
        logger.info("Finished downloading all available replays.")
        logger.separator()
        helpers.remove_lock()
    except Exception as e:
        logger.error('Could not save replay: {:s}'.format(str(e)))
        logger.separator()
        helpers.remove_lock()
    except KeyboardInterrupt:
        logger.separator()
        logger.binfo('The download has been aborted by the user, exiting.')
        logger.separator()
        try:
            shutil.rmtree(pil.live_folder_path)
        except Exception as e:
            logger.error("Could not remove segment folder: {:s}".format(str(e)))
        helpers.remove_lock()


def download_following():
    try:
        logger.info("Checking following users for any livestreams or replays.")
        broadcast_f_list = pil.ig_api.reels_tray()
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
        logger.separator()
        if usernames_available:
            logger.info("The following users have available livestreams or replays:")
            logger.info(', '.join(usernames_available))
            logger.separator()
            for user in usernames_available:
                try:
                    if os.path.isfile(os.path.join(pil.dl_path, user + '.lock')):
                        logger.warn("Lock file is already present for '{:s}', there is probably another download "
                                    "ongoing!".format(user))
                        logger.warn("If this is not the case, manually delete the file '{:s}' and try again.".format(user + '.lock'))
                    else:
                        logger.info("Launching daemon process for '{:s}'.".format(user))
                        start_result = helpers.run_command("pyinstalive -d {:s} -cp '{:s}' -dp '{:s}'".format(user, pil.config_path, pil.dl_path))
                        if start_result:
                            logger.warn("Could not start processs: {:s}".format(str(start_result)))
                        else:
                            logger.info("Process started successfully.")
                    logger.separator()
                    time.sleep(2)
                except Exception as e:
                    logger.warn("Could not start processs: {:s}".format(str(e)))
                except KeyboardInterrupt:
                    logger.binfo('The process launching has been aborted by the user.')
                    logger.separator()
        else:
            logger.info("There are currently no available livestreams or replays.")
            logger.separator()
    except Exception as e:
        logger.error("Could not finish checking following users: {:s}".format(str(e)))
    except KeyboardInterrupt:
        logger.separator()
        logger.binfo('The checking process has been aborted by the user.')
        logger.separator()


def get_live_comments(comments_json_file):
    try:
        comments_downloader = CommentsDownloader(destination_file=comments_json_file)
        first_comment_created_at = 0

        try:
            while not pil.broadcast_downloader.is_aborted:
                if 'initial_buffered_duration' not in pil.livestream_obj and pil.broadcast_downloader.initial_buffered_duration:
                    pil.livestream_obj['initial_buffered_duration'] = pil.broadcast_downloader.initial_buffered_duration
                    comments_downloader.broadcast = pil.livestream_obj
                first_comment_created_at = comments_downloader.get_live(first_comment_created_at)
        except ClientError as e:
            if not 'media has been deleted' in e.error_response:
                logger.warn("Comment collection ClientError: %d %s" % (e.code, e.error_response))

        try:
            if comments_downloader.comments:
                comments_downloader.save()
                comments_log_file = comments_json_file.replace('.json', '.log')
                comment_errors, total_comments = CommentsDownloader.generate_log(
                    comments_downloader.comments, pil.epochtime, comments_log_file,
                    comments_delay=pil.broadcast_downloader.initial_buffered_duration)
                if len(comments_downloader.comments) == 1:
                    logger.info("Successfully saved 1 comment.")
                    os.remove(comments_json_file)
                    logger.separator()
                    return True
                else:
                    if comment_errors:
                        logger.warn(
                            "Successfully saved {:s} comments but {:s} comments are (partially) missing.".format(
                                str(total_comments), str(comment_errors)))
                    else:
                        logger.info("Successfully saved {:s} comments.".format(str(total_comments)))
                    os.remove(comments_json_file)
                    logger.separator()
                    return True
            else:
                logger.info("There are no available comments to save.")
                logger.separator()
                return False
        except Exception as e:
            logger.error('Could not save comments: {:s}'.format(str(e)))
            return False
    except KeyboardInterrupt as e:
        logger.binfo("Downloading livestream comments has been aborted.")
        return False


def get_replay_comments(comments_json_file):
    try:
        comments_downloader = CommentsDownloader(destination_file=comments_json_file)
        comments_downloader.get_replay()
        try:
            if comments_downloader.comments:
                comments_log_file = comments_json_file.replace('.json', '.log')
                comment_errors, total_comments = CommentsDownloader.generate_log(
                    comments_downloader.comments, pil.livestream_obj.get('published_time'), comments_log_file,
                    comments_delay=0)
                if total_comments == 1:
                    logger.info("Successfully saved 1 comment to logfile.")
                    os.remove(comments_json_file)
                    logger.separator()
                    return True
                else:
                    if comment_errors:
                        logger.warn(
                            "Successfully saved {:s} comments but {:s} comments are (partially) missing.".format(
                                str(total_comments), str(comment_errors)))
                    else:
                        logger.info("Successfully saved {:s} comments.".format(str(total_comments)))
                    os.remove(comments_json_file)
                    logger.separator()
                    return True
            else:
                logger.info("There are no available comments to save.")
                return False
        except Exception as e:
            logger.error('Could not save comments to logfile: {:s}'.format(str(e)))
            return False
    except KeyboardInterrupt as e:
        logger.binfo("Downloading replay comments has been aborted.")
        return False
