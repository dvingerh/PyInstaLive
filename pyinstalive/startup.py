import argparse
import configparser
import os
import logging


from . import globals
from . import logger
from . import helpers
from . import assembler
from .constants import Constants
from .session import Session
from .download import Download
from .comments import Comments

def validate_settings():
    try:
        validate_succeeded = True

        if globals.args.config_path:
            if os.path.isfile(globals.args.config_path):
                globals.config.config_path = globals.args.config_path
                logger.binfo("The configuration file path has been overridden.", pre_config=True)
                logger.separator(pre_config=True)
            else:
                logger.warn("The specified configuration file path does not exist.", pre_config=True)    
                logger.warn("Falling back to default path: {:s}".format(globals.config.config_path), pre_config=True)
                logger.separator(pre_config=True)
        elif not os.path.isfile(globals.config.config_path):
            helpers.new_config()
            validate_succeeded = False

        if globals.args.download:
            if globals.args.download_following:
                logger.warn("Only one download method at a time is permitted.", pre_config=True)
                logger.separator(pre_config=True)
                validate_succeeded = False

        elif not globals.args.clean and not globals.args.info and not globals.args.save_video_path and not globals.args.save_comments_path and not globals.args.download_following and not globals.args.organize:
            logger.error("Please specify a download method.", pre_config=True)
            logger.separator(pre_config=True)
            validate_succeeded = False

        if validate_succeeded:
            globals.config.config_path = os.path.realpath(globals.config.config_path)
            globals.config.parser_object.read(globals.config.config_path)
            globals.config.username = globals.config.parser_object.get("pyinstalive", "username")
            globals.config.password = globals.config.parser_object.get("pyinstalive", "password")
            globals.config.log_to_file = globals.config.parser_object.getboolean("pyinstalive", "log_to_file")
            globals.config.download_comments = globals.config.parser_object.getboolean("pyinstalive", "download_comments")
            globals.config.show_session_expires = globals.config.parser_object.getboolean("pyinstalive", "show_session_expires")
            globals.config.clear_temp_files = globals.config.parser_object.getboolean("pyinstalive", "clear_temp_files")
            globals.config.no_assemble = globals.config.parser_object.getboolean("pyinstalive", "no_assemble")
            globals.config.use_locks = globals.config.parser_object.getboolean("pyinstalive", "use_locks")
            globals.config.cmd_on_started = globals.config.parser_object.get("pyinstalive", "cmd_on_started")
            globals.config.cmd_on_ended = globals.config.parser_object.get("pyinstalive", "cmd_on_ended")
            globals.config.ffmpeg_path = globals.config.parser_object.get("pyinstalive", "ffmpeg_path")

            if globals.args.download:
                globals.download = Download(globals.args.download)
                if globals.config.download_comments:
                    globals.comments = Comments()

        return validate_succeeded
    except Exception as e:
        logger.error("Could not process the configuration file: {:s}".format(str(e)))
        logger.error("Ensure the configuration file and given arguments are valid and try again.")
        logger.separator()
        return False
    except KeyboardInterrupt:
        logger.binfo('The process was aborted by the user.')
        logger.separator()
        return False

def run():
    logging.disable()
    globals.init()
    globals.config.parser_object = configparser.ConfigParser()

    logger.banner(no_log=True, pre_config=True)

    parser = argparse.ArgumentParser(description="Running PyInstaLive {:s} using Python {:s}".format(Constants.SCRIPT_VERSION, Constants.PYTHON_VERSION))

    parser.add_argument('-u', '--username', dest='username', type=str, required=False, help="Instagram username to login with.")
    parser.add_argument('-p', '--password', dest='password', type=str, required=False, help="Instagram password to login with.")
    parser.add_argument('-d', '--download', dest='download', type=str, required=False, help="Instagram username of the user to download a livestream from.")
    parser.add_argument('-i', '--info', dest='info', action='store_true', help="Shows information about PyInstaLive.")
    parser.add_argument('-cl', '--clean', dest='clean', action='store_true', help="Cleans the current download path of all leftover files.")
    parser.add_argument('-cp', '--config-path', dest='config_path', type=str, required=False, help="Path to a configuration file.")
    parser.add_argument('-dp', '--download-path', dest='download_path', type=str, required=False, help="Path to a folder to download livestreams to.")
    parser.add_argument('-sc', '--save-comments', dest='save_comments_path', type=str, required=False, help="Path to livestream data JSON file.")
    parser.add_argument('-sv', '--save-video', dest='save_video_path', type=str, required=False, help="Path to livestream data JSON file or path to livestream data folder.")
    parser.add_argument('-df', '--download-following', dest='download_following', action='store_true',help="Check for available livestreams by users the authenticated account is following.")
    parser.add_argument('-na', '--no-assemble', dest='no_assemble', action='store_true', help="Do not assemble the downloaded livestream data files.")
    parser.add_argument('-o', '--organize', action='store_true', help="Move downloaded livestream videos and data files into their own folder, sorted by username.")

    globals.args, unknown_args = parser.parse_known_args()  # Parse arguments
    
    if unknown_args:
        logger.warn("The following unknown argument(s) were provided and will be ignored.", pre_config=True)
        logger.warn('    ' + ' '.join(unknown_args), pre_config=True)
        logger.separator(pre_config=True)

    validate_success = validate_settings()
    if globals.config.log_to_file:
        logger._log_to_file(None, pre_config=True)

    
    if validate_success:
        if globals.args.download or globals.args.download_following:
            globals.session = Session(username=globals.config.username, password=globals.config.password)
            login_success = False

            if not globals.args.username and not globals.args.password:
                login_success = globals.session.authenticate()
            elif (globals.args.username and not globals.args.password) or (globals.args.password and not globals.args.username):
                logger.warn("Missing --username or --password argument.")
                logger.warn("Falling back to the configuration file values.")
                logger.separator()
                login_success = globals.session.authenticate()
            elif globals.args.username and globals.args.password:
                login_success = globals.session.authenticate(username=globals.args.username, password=globals.args.password)

            if login_success:
                globals.download.start()

        elif globals.args.save_video_path:
            assembler.assemble()
            logger.separator()
        elif globals.args.save_comments_path:
            Comments().generate_log()
            logger.separator()