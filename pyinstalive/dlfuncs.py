from json.decoder import JSONDecodeError
import os
import json
import threading
import time
from instagram_private_api_extensions import live


try:
    import logger
    import helpers
    import pil
    import dlfuncs
    import assembler
    from constants import Constants
except ImportError:
    from . import logger
    from . import helpers
    from . import pil
    from . import assembler
    from . import dlfuncs
    from .constants import Constants


def get_broadcasts_tray():
    response = pil.ig_api.get(Constants.REELS_TRAY_URL)
    response_json = json.loads(response.text)
    return response_json

def assemble_segments():
    try:
        if pil.cmd_on_ended:
            try:
                thread = threading.Thread(target=helpers.run_command, args=(pil.cmd_on_ended,))
                thread.daemon = True
                thread.start()
                logger.binfo("Launched finish command: {:s}".format(pil.cmd_on_ended))
            except Exception as e:
                logger.warn('Could not launch finish command: {:s}'.format(str(e)))

        live_mp4_file = '{}{}_{}_{}_{}_live.mp4'.format(pil.dl_path, pil.datetime_compat, pil.dl_user,
                                                     pil.initial_livestream_obj.get('broadcast_id'), pil.epochtime)

        live_segments_path = os.path.normpath(pil.livestream_downloader.output_dir)

        logger.info("Waiting for background threads to finish.")
        if pil.json_thread_worker and pil.heartbeat_info_thread_worker:
            pil.kill_threads = True
            pil.json_thread_worker.join()
            pil.heartbeat_info_thread_worker.join()


        if pil.dl_comments:
            logger.separator()
            logger.info("Generating comments text file.")
            comment_errors, total_comments = helpers.generate_log(pil.comments, live_mp4_file.replace("live.mp4", "comments.txt"),  False)
            logger.separator()
            if len(pil.comments) == 1:
                logger.info("Successfully saved 1 comment.")
                logger.separator()
            elif len(pil.comments) > 1:
                if comment_errors:
                    logger.warn("Successfully saved {:s} comments but {:s} comments might be (partially) incomplete.".format(str(total_comments), str(comment_errors)))
                else:
                    logger.info("Successfully saved {:s} comments.".format(str(total_comments)))
                logger.separator()
            else:
                logger.info("There are no available comments to save.")
                logger.separator()
        else:
            logger.separator()


        try:
            if not pil.skip_assemble:
                logger.info('Assembling downloaded files into video.')
                pil.assemble_arg = live_mp4_file.replace(".mp4", "_downloads")
                if assembler.assemble(user_called=False):
                    logger.separator()
                    logger.info('Saved video: %s' % os.path.basename(live_mp4_file))
                else:
                    logger.error("No video could be created.")
                if pil.clear_temp_files:
                    helpers.remove_temp_folder()
            else:
                logger.binfo("Assembling of downloaded files has been disabled.")
                logger.binfo("Use --assemble command to manually assemble downloaded files.")
            helpers.remove_lock()
        except ValueError as e:
            logger.separator()
            logger.error('Could not assemble downloaded files: {:s}'.format(str(e)))
            if os.listdir(live_segments_path):
                logger.separator()
                logger.binfo("Segment directory is not empty. Trying to assemble again.")
                logger.separator()
                pil.assemble_arg = live_mp4_file.replace(".mp4", "_downloads")
                assembler.assemble(user_called=False)
            else:
                logger.separator()
                logger.error("Segment directory is empty. There is nothing to assemble.")
                logger.separator()
            helpers.remove_lock()
        except Exception as e:
            logger.error('Could not assemble downloaded files: {:s}'.format(str(e)))
            helpers.remove_lock()
    except KeyboardInterrupt:
        logger.separator()
        logger.binfo('The assembling process was aborted by the user.')
        helpers.remove_lock()



def download_livestream():
    try:
        mpd_url = pil.initial_livestream_obj.get('broadcast_dict').get('dash_abr_playback_url')

        pil.live_folder_path = '{}{}_{}_{}_{}_live_downloads'.format(pil.dl_path, pil.datetime_compat, pil.dl_user,
                                                     pil.initial_livestream_obj.get('broadcast_id'), pil.epochtime)
        pil.livestream_downloader = live.Downloader(
            mpd=mpd_url,
            output_dir=pil.live_folder_path,
            max_connection_error_retry=3,
            duplicate_etag_retry=30,
            mpd_download_timeout=3,
            download_timeout=3,
            callback_check=helpers.print_heartbeat,
            ffmpeg_binary=pil.ffmpeg_path)
        pil.livestream_downloader.stream_id = pil.initial_livestream_obj.get('broadcast_id')
    except Exception as e:
        logger.error('Could not start downloading livestream: {:s}'.format(str(e)))
        logger.separator()
        helpers.remove_lock()
    try:
        livestream_owner = pil.initial_livestream_obj.get('broadcast_dict', {}).get('broadcast_owner').get("username")
        try:
            livestream_guest = pil.initial_livestream_obj.get('broadcast_dict', {}).get('cobroadcasters')[0].get("username")
        except Exception:
            livestream_guest = None
        if livestream_owner != pil.dl_user:
            logger.separator()
            logger.binfo('This livestream is a duo-live, the host is "{}".'.format(livestream_owner))
            livestream_guest = None
        if livestream_guest:
            logger.separator()
            logger.binfo('This livestream is a duo-live, the current guest is "{}".'.format(livestream_guest))
            pil.has_guest = livestream_guest
        helpers.create_lock_folder()
        logger.separator()
        helpers.print_durations()
        helpers.print_heartbeat()
        logger.separator()
        logger.info('Downloading livestream, press [CTRL+C] to abort.')

        pil.json_thread_worker = threading.Thread(target=helpers.do_json_generation)
        pil.json_thread_worker.daemon = True
        pil.json_thread_worker.start()

        pil.heartbeat_info_thread_worker = threading.Thread(target=helpers.do_heartbeat)
        pil.heartbeat_info_thread_worker.daemon = True
        pil.heartbeat_info_thread_worker.start()


        if pil.cmd_on_started:
            try:
                thread = threading.Thread(target=helpers.run_command, args=(pil.cmd_on_started,))
                thread.daemon = True
                thread.start()
                logger.binfo("Launched start command: {:s}".format(pil.cmd_on_started))
            except Exception as e:
                logger.warn('Could not launch start command: {:s}'.format(str(e)))
        pil.livestream_downloader.run()
        logger.separator()
        logger.info("The livestream has been ended by the host.")
        logger.separator()
        helpers.print_durations(True)
        logger.separator()
        assemble_segments()
    except KeyboardInterrupt:
        logger.separator()
        logger.binfo('The livestream download was aborted by the user.')
        logger.separator()
        helpers.print_durations(True)
        logger.separator()
        if not pil.livestream_downloader.is_aborted:
            pil.livestream_downloader.stop()
        assemble_segments()

def get_livestreams_info():
    try:
        livestream_list = dlfuncs.get_broadcasts_tray()
        final_livestream_username = None
        if livestream_list.get("broadcasts", None):
            for livestream in livestream_list.get("broadcasts", None):
                owner_username = livestream.get("broadcast_owner", None).get("username", None)
                try:
                    guest_username = livestream.get("cobroadcasters", None)[0].get("username", None)
                except:
                    guest_username = None
                if (pil.dl_user == owner_username) or (pil.dl_user == guest_username):
                    final_livestream_username = owner_username
                    break
        else:
            return False
        if final_livestream_username != None:
            response = pil.ig_api.get(Constants.livestream_info_URL.format(final_livestream_username))
            pil.initial_livestream_obj = json.loads(response.text)
            if pil.initial_livestream_obj.get("broadcast_id", None):
                return True
            else:
                return False
        else:
            return False
        
    except (JSONDecodeError, IndexError):
        return False
    except KeyboardInterrupt:
        return None


def download_following():
    try:
        logger.info("Checking following users for available livestreams.")
        livestream_list = dlfuncs.get_broadcasts_tray()

        usernames_available_livestreams = []
        if livestream_list['broadcasts']:
            for livestream in livestream_list['broadcasts']:
                username = livestream['broadcast_owner']['username']
                if username not in usernames_available_livestreams:
                    usernames_available_livestreams.append(username)

        logger.separator()
        available_total = list(usernames_available_livestreams)
        if available_total:
            logger.info("There are {} available livestreams.".format(str(len(available_total))))
            logger.info(', '.join(available_total))
            logger.separator()
            iterate_users(available_total)
        else:
            logger.info("There are currently no available livestreams.")
            logger.separator()
    except Exception as e:
        logger.error("Could not finish checking following users: {:s}".format(str(e)))
    except KeyboardInterrupt:
        logger.separator()
        logger.binfo('The checking process was aborted by the user.')
        logger.separator()


def iterate_users(user_list):
    for user in user_list:
        try:
            if os.path.isfile(os.path.join(pil.dl_path, user + '.lock')):
                logger.warn("Lock file already exists for user: {:s}".format(user + '.lock'))
                logger.warn("If there is no download ongoing please delete the file and try again.".format(user + '.lock'))
            else:
                logger.info("Launching daemon process for user: {:s}".format(user))
                start_result = helpers.run_command("{:s} -d {:s} -cp '{:s}' -dp '{:s}' {:s}".format(
                    ("'" + pil.winbuild_path + "'") if pil.winbuild_path else "pyinstalive",
                    user,
                    pil.config_path,
                    pil.dl_path,
                    '--username {:s} --password {:s}'.format(pil.ig_user, pil.ig_pass) if pil.config_login_overridden else ''))
                if start_result:
                    logger.warn("Could not start process: {:s}".format(str(start_result)))
                else:
                    logger.info("Process started successfully.")
            logger.separator()
            time.sleep(2)
        except Exception as e:
            logger.warn("Could not start process: {:s}".format(str(e)))
        except KeyboardInterrupt:
            logger.binfo('The process launching was aborted by the user.')
            logger.separator()
            break


