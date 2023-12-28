from . import helpers
from . import logger
from . import globals
from . import api
from . import assembler
from . import live
from .constants import Constants

import json
import threading
import os
import time

class Download:
    def __init__(self, download_user=None):
        self.download_user = download_user
        self.download_user_id = None
        self.timestamp = helpers.strepochtime()
        self.video_path = None
        self.segments_path = None
        self.data_json_path = None
        self.livestream_object_init = None
        self.livestream_object = None
        self.downloader_object = None
        self.livestream_guest = None
        self.livestream_owner = None
        self.tasks_worker = None
        self.download_stop = False

    def start(self):
        if globals.args.download:
            checking_self = self.download_user == globals.session.username
            if checking_self:
                logger.warn("Login with a different account to download your own livestreams.")
                logger.separator()
                return
            if not helpers.lock_exists():
                helpers.lock_create(lock_type="user")
                logger.info('Getting livestream information for user: {:s}'.format(self.download_user))
                user_info = api.get_user_info().get("data", {}).get("user", None)
                if user_info:
                    self.download_user_id = user_info.get("id", None)
                if not self.download_user_id:
                    logger.separator()
                    logger.warn("The specified user does not exist.")
                    logger.separator()
                    return
                self.livestream_object_init = self.get_single_livestream()
                logger.separator()
                if self.livestream_object_init:
                    logger.binfo("Livestream available, starting download.")
                    self.download_livestream()
                elif self.livestream_object_init == False:
                    logger.binfo('There is currently no available livestream.')
                elif not self.livestream_object_init:
                    pass

                logger.separator()
            else:
                logger.warn("Lock file is already present for this user, there is probably another download ongoing.")
                logger.warn("If this is not the case, manually delete the file '{:s}' and try again.".format(self.download_user + '.lock'))
                logger.separator()
        elif globals.args.download_following:
            self.get_following_livestreams()

    def get_following_livestreams(self):
        try:
            livestream_list = api.get_reels_tray()
            usernames_available_livestreams = []
            if livestream_list.get("broadcasts", None):
                for livestream in livestream_list.get("broadcasts", None):
                    owner_username = livestream.get("broadcast_owner", None).get("username", None)
                    if owner_username:
                        usernames_available_livestreams.append(owner_username)
                if usernames_available_livestreams:
                    logger.info("The following users have available livestreams:")
                    logger.info(', '.join(usernames_available_livestreams))
                    logger.separator()
                    self.iterate_users(usernames_available_livestreams)
                else:
                    logger.info("There are currently no available livestreams.")
                    logger.separator()
            else:
                return False
        except Exception as e:
            logger.error("Could not get livestream information: {:s}".format(str(e)))
            logger.separator()
            return None
        except KeyboardInterrupt:
            logger.binfo('The process was aborted by the user.')
            logger.separator()
            return None

    def iterate_users(self, user_list):
        for index, user in enumerate(user_list):
            try:
                if os.path.isfile(os.path.join(globals.config.download_path, user + '.lock')):
                    logger.warn("Lock file is already present for '{:s}', there is probably another download ongoing.".format(user))
                    logger.warn("If this is not the case, manually delete the file '{:s}' and try again.".format(user + '.lock'))
                else:
                    logger.info("Starting download for '{:s}'.".format(user))
                    start_result = helpers.run_command("pyinstalive -d {:s}".format(user))
                    if start_result:
                        logger.warn("Could not start download: {:s}".format(str(start_result)))
                    else:
                        logger.info("Successfully started download.")
                logger.separator()
                if index != len(user_list) - 1:
                    time.sleep(2)
            except Exception as e:
                logger.warn("Could not start download: {:s}".format(str(e)))
            except KeyboardInterrupt:
                logger.binfo('The process has been aborted by the user.')
                logger.separator()
                break

    def download_livestream(self):
        try:
            mpd_url = self.livestream_object_init.get('dash_abr_playback_url')

            self.video_path = os.path.join(globals.config.download_path, '{}_{}_{}_{}_live.mp4'.format(helpers.strdatetime_compat(), self.download_user,
                                                        self.livestream_object_init.get('id'), self.timestamp))

            self.segments_path = os.path.join(globals.config.download_path, '{}_{}_{}_{}_live'.format(helpers.strdatetime_compat(), self.download_user,
                                                        self.livestream_object_init.get('id'), self.timestamp))

            self.data_generate_comments_path = os.path.join(globals.config.download_path, '{}_{}_{}_{}_live.log'.format(helpers.strdatetime_compat(), self.download_user,
                                                        self.livestream_object_init.get('id'), self.timestamp))

            self.data_json_path = os.path.join(globals.config.download_path, '{}_{}_{}_{}_live.json'.format(helpers.strdatetime_compat(), self.download_user,
                                                        self.livestream_object_init.get('id'), self.timestamp))
                                                       
            self.downloader_object = live.Downloader(
                mpd=mpd_url,
                output_dir=self.segments_path,
                max_connection_error_retry=3,
                duplicate_etag_retry=30,
                mpd_download_timeout=3,
                callback_check=self.update_stream_data,
                download_timeout=3,
                ffmpeg_binary=globals.config.ffmpeg_path)

            self.livestream_owner = self.livestream_object_init.get('broadcast_owner').get("username")
            try:
                self.livestream_guest = self.livestream_object_init.get('cobroadcasters')[0].get("username")
            except Exception:
                self.livestream_guest = None
            if self.livestream_owner != self.download_user:
                logger.separator()
                logger.binfo('This livestream is a duo-live. The host is: {}'.format(self.livestream_owner))
                self.livestream_guest = None
            if self.livestream_guest:
                logger.separator()
                logger.binfo('This livestream is a duo-live. The current guest is: {}'.format(self.livestream_guest))
            logger.separator()
            if globals.config.cmd_on_started:
                try:
                    thread = threading.Thread(target=helpers.run_command, args=(globals.config.cmd_on_started,))
                    thread.daemon = True
                    thread.start()
                    logger.binfo("Executed start command: {:s}".format(globals.config.cmd_on_started))
                    logger.separator()
                except Exception as e:
                    logger.warn('Could not execute start command: {:s}'.format(str(e)))
                    logger.separator()
            logger.info('Downloading livestream, press [CTRL+C] to abort.')
            logger.separator()
            self.update_stream_data()
            self.tasks_worker = threading.Thread(target=helpers.handle_tasks_worker)
            self.tasks_worker.daemon = True
            self.tasks_worker.start()

            self.downloader_object.run()
            logger.separator()
            logger.binfo("The livestream has been ended.")
            logger.separator()
            helpers.print_durations()
            logger.separator()
            self.finish_download()
        except Exception as e:
            logger.separator()
            logger.error("Could not complete the livestream download: " + str(e))
        except KeyboardInterrupt:
            logger.separator()
            logger.binfo('The process was aborted by the user.')
            logger.separator()
            helpers.print_durations()
            logger.separator()
            if not self.downloader_object.is_aborted:
                self.downloader_object.stop()
            self.finish_download()

    def finish_download(self):
        try:
            self.livestream_object['initial_buffered_duration'] = self.downloader_object.initial_buffered_duration
            if globals.config.cmd_on_ended:
                try:
                    thread = threading.Thread(target=helpers.run_command, args=(globals.config.cmd_on_ended,))
                    thread.daemon = True
                    thread.start()
                    logger.binfo("Executed end command: {:s}".format(globals.config.cmd_on_ended))
                    logger.separator()
                except Exception as e:
                    logger.warn('Could not execute end command: {:s}'.format(str(e)))
                    logger.separator()
                    
            logger.info("Waiting for background tasks to finish.")
            self.download_stop = True
            if self.tasks_worker:
                self.tasks_worker.join()
            logger.separator()


            if globals.config.download_comments:
                globals.comments.generate_log()
                logger.separator()

            if not globals.config.no_assemble:
                assembler.assemble()
                if globals.config.clear_temp_files:
                    helpers.remove_temp_folder()
            else:
                logger.binfo("Assembling of collected segment files has been disabled.")
        except KeyboardInterrupt:
            logger.binfo('The process was aborted by the user.')

    def get_single_livestream(self):
        try:
            initial_livestream_obj = api.get_single_live()
            if initial_livestream_obj.get("message", None) != None:
                if initial_livestream_obj.get("message") == "User is not live":
                    initial_livestream_obj = None
            if initial_livestream_obj:
                return initial_livestream_obj
            else:
                return False
        except Exception as e:
            logger.error("Could not get livestream information: {:s}".format(str(e)))
            logger.separator()
            return None
        except KeyboardInterrupt:
            logger.binfo('The process was aborted by the user.')
            logger.separator()
            return None

    def get_guest_status(self):
        guests = api.get_stream_data().get("cobroadcasters", {})
        for guest in guests:
            try:
                livestream_guest = guest.get('username')
            except Exception:
                livestream_guest = None
            if livestream_guest and not self.livestream_guest:
                logger.separator()
                self.livestream_guest = livestream_guest
                logger.binfo('The livestream host has started guesting with user: {}'.format(self.livestream_guest))
            if not livestream_guest and self.livestream_guest:
                logger.separator()
                logger.binfo('The livestream host has stopped guesting with user: {}'.format(self.livestream_guest))
                if self.livestream_guest == self.download_user:
                    self.downloader_object.stop()
                self.livestream_guest = None

    def update_stream_data(self, from_thread=False):
        if not self.download_stop:
            if not self.livestream_object:
                self.livestream_object = api.get_stream_data()
                if not self.livestream_object.get("initial_buffered_duration", None):
                    self.livestream_object['initial_buffered_duration'] = self.downloader_object.initial_buffered_duration
                self.livestream_object["delay"] = int(globals.download.timestamp) - int(self.livestream_object.get("published_time"))

            last_stream_status = self.livestream_object.get("broadcast_status")
            stream_heartbeat = api.do_heartbeat() if globals.config.send_heartbeat else api.get_stream_data()
            stream_status = stream_heartbeat.get("broadcast_status")
            if stream_heartbeat.get("status") == "fail":
                logger.separator()
                logger.error('The livestream host has possibly lost connection with Instagram.')
                self.download_stop = True
                self.downloader_object.stop()
                return False

            self.livestream_object["broadcast_status"] = stream_status
            self.livestream_object["viewer_count"] = stream_heartbeat.get("viewer_count")
            if globals.config.download_comments:
                globals.comments.retrieve_comments()
            helpers.write_data_json()
            if from_thread and len(stream_heartbeat.get("cobroadcasters", [])) > 0:
                self.get_guest_status()
            if not from_thread or (last_stream_status != stream_status):
                if from_thread:
                    logger.separator()
                logger.info('Airing time  : {}'.format(helpers.get_stream_duration("airtime")))
                logger.info('Status       : {}'.format(self.livestream_object.get("broadcast_status", "?").capitalize()))
                logger.info('Viewers      : {}'.format( int(self.livestream_object.get("viewer_count", "?"))))
            return self.livestream_object.get('broadcast_status') not in ['active', 'interrupted']
