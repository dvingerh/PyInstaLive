from json.decoder import JSONDecodeError
import os
import json
import threading
import time
from typing import final
from instagram_private_api_extensions import live
from xml.dom.minidom import parseString


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

        live_mp4_file = '{}{}_{}_{}_{}_live.mp4'.format(pil.dl_path, pil.datetime_compat, pil.dl_user,
                                                     pil.initial_broadcast_obj.get('broadcast_id'), pil.epochtime)

        live_segments_path = os.path.normpath(pil.broadcast_downloader.output_dir)

        pil.kill_threads = True
        logger.info("Waiting for threads to finish.")
        if pil.json_thread_worker and pil.json_thread_worker.is_alive():
            pil.json_thread_worker.join()
        if pil.heartbeat_info_thread_worker and pil.heartbeat_info_thread_worker.is_alive():
            pil.heartbeat_info_thread_worker.join()
        try:
            if not pil.skip_merge:
                logger.info('Merging downloaded files into video.')
                pil.assemble_arg = live_mp4_file.replace(".mp4", "_downloads")
                assembler.assemble(user_called=False)
                logger.info('Successfully merged downloaded files into video.')
                if pil.clear_temp_files:
                    helpers.remove_temp_folder()
            else:
                logger.binfo("Merging of downloaded files has been disabled.")
                logger.binfo("Use --assemble command to manually merge downloaded segments.")
            helpers.remove_lock()
        except ValueError as e:
            logger.separator()
            logger.error('Could not merge downloaded files: {:s}'.format(str(e)))
            if os.listdir(live_segments_path):
                logger.separator()
                logger.binfo("Segment directory is not empty. Trying to merge again.")
                logger.separator()
                pil.assemble_arg = live_mp4_file.replace(".mp4", "_downloads")
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
        mpd_url = pil.initial_broadcast_obj.get('broadcast_dict').get('dash_playback_url')

        pil.live_folder_path = '{}{}_{}_{}_{}_live_downloads'.format(pil.dl_path, pil.datetime_compat, pil.dl_user,
                                                     pil.initial_broadcast_obj.get('broadcast_id'), pil.epochtime)
        pil.broadcast_downloader = live.Downloader(
            mpd=mpd_url,
            output_dir=pil.live_folder_path,
            max_connection_error_retry=3,
            duplicate_etag_retry=30,
            mpd_download_timeout=3,
            download_timeout=3,
            callback_check=helpers.print_heartbeat,
            ffmpeg_binary=pil.ffmpeg_path)
        pil.broadcast_downloader.stream_id = pil.initial_broadcast_obj.get('broadcast_id')
    except Exception as e:
        logger.error('Could not start downloading livestream: {:s}'.format(str(e)))
        logger.separator()
        helpers.remove_lock()
    try:
        broadcast_owner = pil.initial_broadcast_obj.get('broadcast_dict', {}).get('broadcast_owner').get("username")
        try:
            broadcast_guest = pil.initial_broadcast_obj.get('broadcast_dict', {}).get('cobroadcasters')[0].get("username")
        except Exception:
            broadcast_guest = None
        if broadcast_owner != pil.dl_user:
            logger.separator()
            logger.binfo('This livestream is a dual-live, the owner is "{}".'.format(broadcast_owner))
            broadcast_guest = None
        if broadcast_guest:
            logger.separator()
            logger.binfo('This livestream is a dual-live, the current guest is "{}".'.format(broadcast_guest))
            pil.has_guest = broadcast_guest
        helpers.create_lock_folder()
        logger.separator()
        helpers.print_durations()
        helpers.print_heartbeat()
        logger.separator()
        logger.info('Downloading livestream, press [CTRL+C] to abort.')

        pil.json_thread_worker = threading.Thread(target=helpers.generate_json_segments)
        pil.json_thread_worker.start()

        pil.heartbeat_info_thread_worker = threading.Thread(target=helpers.do_heartbeat)
        pil.heartbeat_info_thread_worker.start()


        if pil.run_at_start:
            try:
                thread = threading.Thread(target=helpers.run_command, args=(pil.run_at_start,))
                thread.daemon = True
                thread.start()
                logger.binfo("Launched start command: {:s}".format(pil.run_at_start))
            except Exception as e:
                logger.warn('Could not launch command: {:s}'.format(str(e)))
        pil.broadcast_downloader.run()
        logger.separator()
        logger.info("The livestream has been ended by the user.")
        logger.separator()
        helpers.print_durations(True)
        logger.separator()
        merge_segments()
    except KeyboardInterrupt:
        logger.separator()
        logger.binfo('The download has been aborted.')
        logger.separator()
        helpers.print_durations(True)
        logger.separator()
        if not pil.broadcast_downloader.is_aborted:
            pil.broadcast_downloader.stop()
            merge_segments()

def get_broadcasts_info():
    try:

        broadcast_f_list = dlfuncs.get_broadcasts_tray()
        open("test.json", "w").write(json.dumps(broadcast_f_list))
        final_broadcast_name = None
        if broadcast_f_list.get("broadcasts", None):
            for broadcast_f in broadcast_f_list.get("broadcasts", None):
                owner_username = broadcast_f.get("broadcast_owner", None).get("username", None)
                try:
                    guest_username = broadcast_f.get("cobroadcasters", None)[0].get("username", None)
                except:
                    guest_username = None
                if (pil.dl_user == owner_username) or (pil.dl_user == guest_username):
                    final_broadcast_name = owner_username
                    break
        if final_broadcast_name != None:
            response = pil.ig_api.get(Constants.BROADCAST_INFO_URL.format(final_broadcast_name))
            pil.initial_broadcast_obj = json.loads(response.text)
            if pil.initial_broadcast_obj.get("broadcast_id", None):
                return True
            else:
                return False
    except (JSONDecodeError, IndexError):
        return False


def download_following():
    try:
        logger.info("Checking following users for any livestreams.")
        broadcast_f_list = dlfuncs.get_broadcasts_tray()

        usernames_available_livestreams = []
        if broadcast_f_list['broadcasts']:
            for broadcast_f in broadcast_f_list['broadcasts']:
                username = broadcast_f['broadcast_owner']['username']
                if username not in usernames_available_livestreams:
                    usernames_available_livestreams.append(username)

        logger.separator()
        available_total = list(usernames_available_livestreams)
        if available_total:
            logger.info("The following users have available livestreams.")
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
        logger.binfo('The checking process has been aborted by the user.')
        logger.separator()


def iterate_users(user_list):
    for user in user_list:
        try:
            if os.path.isfile(os.path.join(pil.dl_path, user + '.lock')):
                logger.warn("Lock file is already present for '{:s}', there is probably another download "
                            "ongoing!".format(user))
                logger.warn(
                    "If this is not the case, manually delete the file '{:s}' and try again.".format(user + '.lock'))
            else:
                logger.info("Launching daemon process for '{:s}'.".format(user))
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
            logger.binfo('The process launching has been aborted by the user.')
            logger.separator()
            break


