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

        elif not globals.args.clean and not globals.args.info and not globals.args.generate_video_path and not globals.args.generate_comments_path and not globals.args.download:
            logger.error("No download method was specified.", pre_config=True)
            logger.separator(pre_config=True)
            validate_succeeded = False

        if validate_succeeded:
            globals.config.config_path = os.path.realpath(globals.config.config_path)
            globals.config.parser_object.read(globals.config.config_path)
            globals.config.username = globals.config.parser_object.get("pyinstalive", "username")
            globals.config.password = globals.config.parser_object.get("pyinstalive", "password")
            globals.config.download_path = globals.config.parser_object.get("pyinstalive", "download_path")
            globals.config.log_to_file = globals.config.parser_object.getboolean("pyinstalive", "log_to_file")
            globals.config.download_comments = globals.config.parser_object.getboolean("pyinstalive", "download_comments")
            globals.config.clear_temp_files = globals.config.parser_object.getboolean("pyinstalive", "clear_temp_files")
            globals.config.no_assemble = globals.config.parser_object.getboolean("pyinstalive", "no_assemble")
            globals.config.use_locks = globals.config.parser_object.getboolean("pyinstalive", "use_locks")
            globals.config.cmd_on_started = globals.config.parser_object.get("pyinstalive", "cmd_on_started")
            globals.config.cmd_on_ended = globals.config.parser_object.get("pyinstalive", "cmd_on_ended")
            globals.config.ffmpeg_path = globals.config.parser_object.get("pyinstalive", "ffmpeg_path")

            if globals.args.download_path:
                globals.config.download_path = globals.args.download_path
                logger.binfo("The download path has been overridden.", pre_config=True)
                logger.separator()
            if not os.path.exists(globals.config.download_path):
                globals.config.download_path = os.getcwd()
                logger.warn("The specified download path does not exist.")
                logger.warn("Falling back to default path: {:s}".format(globals.config.download_path))
                logger.separator()

            if globals.config.ffmpeg_path:
                if not os.path.isfile(globals.config.ffmpeg_path):
                    logger.warn("The specified path to the FFmpeg framework does not exist.")
                    globals.config.ffmpeg_path = os.getenv('FFMPEG_BINARY', 'ffmpeg')
                    if helpers.command_exists(globals.config.ffmpeg_path):
                        logger.warn("Falling back to environment variable.")
                        logger.separator()
                    else:
                        logger.separator()
                        logger.error("Could not find the required FFmpeg framework.")
                        validate_succeeded = False
                        logger.separator()
            else:
                globals.config.ffmpeg_path = os.getenv('FFMPEG_BINARY', 'ffmpeg')
                if not helpers.command_exists(globals.config.ffmpeg_path):
                    logger.error("Could not find the required FFmpeg framework.")
                    validate_succeeded = False
                    logger.separator()
        

            if globals.args.download:
                globals.download = Download(globals.args.download)
                if globals.config.download_comments:
                    globals.comments = Comments()

            if globals.args.no_assemble:
                globals.config.no_assemble = True

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
    parser.add_argument('-cl', '--clean', dest='clean', action='store_true', help="Clean the current download path of all leftover files.")
    parser.add_argument('-cp', '--config-path', dest='config_path', type=str, required=False, help="Override the default configuration file path.")
    parser.add_argument('-dp', '--download-path', dest='download_path', type=str, required=False, help="Override the default download path.")
    parser.add_argument('-dc', '--download-comments', dest='download_comments', type=str, required=False, help="Download livestream comments. Overrides the configuration file setting.")
    parser.add_argument('-gc', '--generate-comments', dest='generate_comments_path', type=str, required=False, help="Generate a comments log file. Requires a ivestream data file.")
    parser.add_argument('-gv', '--generate-video', dest='generate_video_path', type=str, required=False, help="Generate a comments log file. Requires a livestream data file or folder.")
    parser.add_argument('-na', '--no-assemble', dest='no_assemble', action='store_true', help="Do not assemble the downloaded livestream data files. Overrides the configuration file setting.")

    globals.args, unknown_args = parser.parse_known_args()  # Parse arguments
    
    if unknown_args:
        logger.warn("The following unknown argument(s) were provided and will be ignored.", pre_config=True)
        logger.warn('    ' + ' '.join(unknown_args), pre_config=True)
        logger.separator(pre_config=True)

    validate_success = validate_settings()
    if globals.config.log_to_file:
        logger._log_to_file(None, pre_config=True)

    
    if validate_success:
        if globals.args.download:
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
                helpers.lock_remove()

        elif globals.args.generate_video_path:
            assembler.assemble()
            logger.separator()
        elif globals.args.generate_comments_path:
            Comments().generate_log()
            logger.separator()
        elif globals.args.clean:
            helpers.clean_download_dir()
            logger.separator()
        elif globals.args.info:
            helpers.show_info()
            logger.separator()
