from . import helpers
from . import logger
from . import globals
from . import api
from . import assembler
from .constants import Constants

from instagram_private_api_extensions import live

import threading
import os
import json

class Download:
    def __init__(self, download_user=""):
        self.download_user = download_user
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
        checking_self = self.download_user == globals.session.username
        if checking_self:
            logger.warn("Login with a different account to download your own livestreams.")
            return
        if not helpers.lock_exists():
            helpers.lock_create(lock_type="user")
            logger.info('Getting livestream information for user: {:s}'.format(self.download_user))

            self.livestream_object_init = self.get_livestreams_info()

            if self.livestream_object_init:
                logger.separator()
                logger.info("Livestream available, starting download.")
                self.download_livestream()
            elif self.livestream_object_init == False:
                logger.separator()
                logger.info('There is currently no available livestream.')
            elif not self.livestream_object_init:
                pass

            logger.separator()
        else:
            logger.warn("Lock file is already present for this user, there is probably another download ongoing.")
            logger.warn("If this is not the case, manually delete the file '{:s}' and try again.".format(self.download_user + '.lock'))
            logger.separator()

    def download_livestream(self):
        try:
            mpd_url = self.livestream_object_init.get('broadcast_dict').get('dash_abr_playback_url')

            self.video_path = os.path.join(globals.config.download_path, '{}_{}_{}_{}_live.mp4'.format(helpers.strdatetime_compat(), self.download_user,
                                                        self.livestream_object_init.get('broadcast_id'), self.timestamp))

            self.segments_path = os.path.join(globals.config.download_path, '{}_{}_{}_{}_live'.format(helpers.strdatetime_compat(), self.download_user,
                                                        self.livestream_object_init.get('broadcast_id'), self.timestamp))

            self.data_generate_comments_path = os.path.join(globals.config.download_path, '{}_{}_{}_{}_live.log'.format(helpers.strdatetime_compat(), self.download_user,
                                                        self.livestream_object_init.get('broadcast_id'), self.timestamp))

            self.data_json_path = os.path.join(globals.config.download_path, '{}_{}_{}_{}_live.json'.format(helpers.strdatetime_compat(), self.download_user,
                                                        self.livestream_object_init.get('broadcast_id'), self.timestamp))
                                                       
            self.downloader_object = live.Downloader(
                mpd=mpd_url,
                output_dir=self.segments_path,
                max_connection_error_retry=3,
                duplicate_etag_retry=30,
                mpd_download_timeout=3,
                download_timeout=3,
                callback_check=self.update_stream_data,
                ffmpeg_binary=globals.config.ffmpeg_path)

            self.livestream_owner = self.livestream_object_init.get('broadcast_dict', {}).get('broadcast_owner').get("username")
            try:
                self.livestream_guest = self.livestream_object_init.get('broadcast_dict', {}).get('cobroadcasters')[0].get("username")
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
            helpers.print_durations()
            self.update_stream_data()
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

            self.tasks_worker = threading.Thread(target=helpers.handle_tasks_worker)
            self.tasks_worker.daemon = True
            self.tasks_worker.start()

            self.downloader_object.run()
            logger.separator()
            logger.info("The livestream has been ended by the host.")
            logger.separator()
            helpers.print_durations(True)
            logger.separator()
            self.finish_download()
        except Exception as e:
            logger.separator()
            logger.error("Could not complete the livestream download: " + str(e))
        except KeyboardInterrupt:
            logger.separator()
            logger.binfo('The process was aborted by the user.')
            logger.separator()
            helpers.print_durations(True)
            logger.separator()
            if not self.downloader_object.is_aborted:
                self.downloader_object.stop()
            self.finish_download()

    def finish_download(self):
        try:
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
            if self.tasks_worker:
                self.download_stop = True
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
                logger.binfo("Use --assemble command to manually assemble downloaded segment files.")
        except KeyboardInterrupt:
            logger.binfo('The process was aborted by the user.')

    def get_livestreams_info(self):
        try:
            livestream_list = api.get_broadcasts_tray()
            final_livestream_username = None
            if livestream_list.get("broadcasts", None):
                for livestream in livestream_list.get("broadcasts", None):
                    owner_username = livestream.get("broadcast_owner", None).get("username", None)
                    try:
                        guest_username = livestream.get("cobroadcasters", None)[0].get("username", None)
                    except:
                        guest_username = None
                    if (globals.download.download_user == owner_username) or (globals.download.download_user == guest_username):
                        final_livestream_username = owner_username
            else:
                return False
            if final_livestream_username != None:
                response = globals.session.session.get(Constants.LIVE_STATE_USER.format(final_livestream_username))
                initial_livestream_obj = json.loads(response.text)
                if initial_livestream_obj.get("broadcast_id", None):
                    return initial_livestream_obj
                else:
                    return False
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

    def check_if_guesting(self):
        try:
            livestream_guest = globals.download.livestream_object.get('cobroadcasters', {})[0].get('username')
        except Exception:
            livestream_guest = None
        if livestream_guest and not globals.download.livestream_guest:
            logger.separator()
            globals.download.livestream_guest = livestream_guest
            logger.binfo('The livestream host has started guesting with user: {}'.format(globals.download.livestream_guest))
        if not livestream_guest and globals.download.livestream_guest:
            logger.separator()
            logger.binfo('The livestream host has stopped guesting with user: {}'.format(globals.download.livestream_guest))
            if globals.download.livestream_guest == globals.download.download_user:
                globals.download.downloader_object.stop()
            globals.download.livestream_guest = None

    def update_stream_data(self, from_thread=False):
        if not globals.download.download_stop:
            if not globals.download.livestream_object:
                previous_state = globals.download.livestream_object_init.get("broadcast_dict").get("broadcast_status")
            else:
                previous_state = globals.download.livestream_object.get("broadcast_status")
            globals.download.livestream_object = api.get_stream_data()
            if globals.config.download_comments:
                globals.comments.retrieve_comments()
            helpers.write_data_json()
            if from_thread:
                self.check_if_guesting()
            if not from_thread or (previous_state != globals.download.livestream_object.get("broadcast_status")):
                if from_thread:
                    logger.separator()
                    helpers.print_durations()
                logger.info('Status       : {}'.format(globals.download.livestream_object.get("broadcast_status").capitalize()))
                logger.info('Viewers      : {}'.format( int(globals.download.livestream_object.get("viewer_count"))))
            return globals.download.livestream_object.get('broadcast_status') not in ['available', 'interrupted']
