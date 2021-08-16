import argparse
import configparser
import os
import sys
import logging
import platform

try:
    import pil
    import auth
    import logger
    import helpers
    import downloader
    import assembler
    import dlfuncs
    import organize
    from constants import Constants
except ImportError:
    from . import pil
    from . import auth
    from . import logger
    from . import helpers
    from . import downloader
    from . import assembler
    from . import dlfuncs
    from . import organize
    from .constants import Constants

def validate_inputs(config, args, unknown_args):
    error_arr = []
    banner_shown = False
    try:
        if args.configpath:
            if os.path.isfile(args.configpath):
                pil.config_path = args.configpath
                logger.binfo("Overriding configuration file path: {:s}".format(pil.config_path))
                logger.separator()
            else:
                logger.banner()
                banner_shown = True
                logger.warn("The specified configuration file path does not exist.")
                logger.warn("Falling back to default path: {:s}".format(pil.config_path))
                pil.config_path = os.path.join(os.getcwd(), "pyinstalive.ini")
                logger.separator()


        if not os.path.isfile(pil.config_path):  # Create new config if it doesn't exist
            if not banner_shown:
                logger.banner()
            helpers.new_config()
            return False
        pil.config_path = os.path.realpath(pil.config_path)
        config.read(pil.config_path)

        if args.download:
            pil.dl_user = args.download
            if args.downloadfollowing or args.batchfile:
                logger.banner()
                logger.warn("Only one download method at a time is permitted.")
                logger.separator()
                return False
        elif not args.clean and not args.info and not args.assemble and not args.downloadfollowing and not args.batchfile and not args.organize:
            logger.banner()
            logger.error("Please specify a download method.")
            logger.separator()
            return False

        if helpers.bool_str_parse(config.get('pyinstalive', 'log_to_file')) == "Invalid":
            pil.log_to_file = True
            error_arr.append(['log_to_file', 'True'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'log_to_file')):
            pil.log_to_file = True
        else:
            pil.log_to_file = False

        logger.banner()

        if args.batchfile:
            if os.path.isfile(args.batchfile):
                pil.dl_batchusers = [user.rstrip('\n') for user in open(args.batchfile)]
                if not pil.dl_batchusers:
                    logger.error("The specified file is empty.")
                    logger.separator()
                    return False
                else:
                    logger.info("Downloading {:d} users from batch file.".format(len(pil.dl_batchusers)))
                    logger.separator()
            else:
                logger.error('The specified file does not exist.')
                logger.separator()
                return False

        if unknown_args:
            pil.uargs = unknown_args
            logger.warn("The following unknown argument(s) were provided and will be ignored.")
            logger.warn('    ' + ' '.join(unknown_args))
            logger.separator()


        pil.ig_user = config.get('pyinstalive', 'username')
        pil.ig_pass = config.get('pyinstalive', 'password')
        pil.dl_path = config.get('pyinstalive', 'download_path')
        pil.run_at_start = config.get('pyinstalive', 'run_at_start')
        pil.run_at_finish = config.get('pyinstalive', 'run_at_finish')
        pil.ffmpeg_path = config.get('pyinstalive', 'ffmpeg_path')
        pil.skip_assemble = config.get('pyinstalive', 'skip_assemble')
        pil.args = args
        pil.config = config

        if args.dlpath:
            pil.dl_path = args.dlpath

        if helpers.bool_str_parse(config.get('pyinstalive', 'download_comments')) == "Invalid":
            pil.dl_comments = False
            error_arr.append(['download_comments', 'True'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'download_comments')):
            pil.dl_comments = True
        else:
            pil.dl_comments = False

        if helpers.bool_str_parse(config.get('pyinstalive', 'show_session_expires')) == "Invalid":
            pil.show_session_expires = False
            error_arr.append(['show_session_expires', 'False'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'show_session_expires')):
            pil.show_session_expires = True
        else:
            pil.show_session_expires = False

        if helpers.bool_str_parse(config.get('pyinstalive', 'skip_assemble')) == "Invalid":
            pil.skip_assemble = False
            error_arr.append(['skip_assemble', 'False'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'skip_assemble')):
            pil.skip_assemble = True
        else:
            pil.skip_assemble = False

        if helpers.bool_str_parse(config.get('pyinstalive', 'use_locks')) == "Invalid":
            pil.use_locks = False
            error_arr.append(['use_locks', 'False'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'use_locks')):
            pil.use_locks = True
        else:
            pil.use_locks = False

        if helpers.bool_str_parse(config.get('pyinstalive', 'clear_temp_files')) == "Invalid":
            pil.clear_temp_files = False
            error_arr.append(['clear_temp_files', 'False'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'clear_temp_files')):
            pil.clear_temp_files = True
        else:
            pil.clear_temp_files = False

        if args.skip_assemble:
            pil.skip_assemble = True

        if pil.ffmpeg_path:
            if not os.path.isfile(pil.ffmpeg_path):
                pil.ffmpeg_path = None
                cmd = "where" if platform.system() == "Windows" else "which"
                logger.warn("The specified FFmpeg file path does not exist.")
                logger.warn("Falling back to the environment variables.")
            else:
                logger.binfo("Overriding FFmpeg binary path: {:s}".format(pil.ffmpeg_path))
        else:
            if not helpers.command_exists('ffmpeg') and not args.info:
                logger.error("Could not find the FFmpeg framework.")
                logger.separator()
                return False

        if not pil.ig_user or not len(pil.ig_user):
            raise Exception("Invalid value for 'username'. This value is required.")

        if not pil.ig_pass or not len(pil.ig_pass):
            raise Exception("Invalid value for 'password'. This value is required.")

        if not pil.dl_path.endswith('/'):
            pil.dl_path = pil.dl_path + '/'
        if not pil.dl_path or not os.path.exists(pil.dl_path):
            pil.dl_path = os.getcwd() + "/"
            if not args.dlpath:
                error_arr.append(['download_path', os.getcwd() + "/"])
            else:
                logger.warn("The specified download path does not exist.")
                logger.warn("Falling back to default path: {:s}".format(pil.dl_path))
                logger.separator()

        if error_arr:
            for error in error_arr:
                logger.warn("Invalid value for entry: {:s}".format(error[0]))
                logger.warn("Falling back to default value: {:s}".format(error[1]))
                logger.separator()

        if args.info:
            helpers.show_info()
            return False
        elif args.clean:
            helpers.clean_download_dir()
            return False
        elif args.assemble:
            pil.assemble_arg = args.assemble
            assembler.assemble()
            return False
        elif args.organize:
            organize.organize_files()
            return False

        return True
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
    pil.initialize()
    logging.disable(logging.CRITICAL)
    config = configparser.ConfigParser()
    parser = argparse.ArgumentParser(
        description="You are running PyInstaLive {:s} using Python {:s}".format(Constants.SCRIPT_VER,
                                                                                Constants.PYTHON_VER))

    parser.add_argument('-u', '--username', dest='username', type=str, required=False,
                        help="Instagram username to login with.")
    parser.add_argument('-p', '--password', dest='password', type=str, required=False,
                        help="Instagram password to login with.")
    parser.add_argument('-d', '--download', dest='download', type=str, required=False,
                        help="The username of the user whose livestream you want to save.")
    parser.add_argument('-b,', '--batch-file', dest='batchfile', type=str, required=False,
                        help="Read a text file of usernames to download livestreams from.")
    parser.add_argument('-i', '--info', dest='info', action='store_true', help="View information about PyInstaLive.")
    parser.add_argument('-cl', '--clean', dest='clean', action='store_true',
                        help="PyInstaLive will clean the current download folder of all leftover files.")
    parser.add_argument('-cp', '--config-path', dest='configpath', type=str, required=False,
                        help="Path to a PyInstaLive configuration file.")
    parser.add_argument('-dp', '--download-path', dest='dlpath', type=str, required=False,
                        help="Path to folder where PyInstaLive should save livestreams.")
    parser.add_argument('-as', '--assemble', dest='assemble', type=str, required=False,
                        help="Path to json file required by the assembler to generate a video file from the segments.")
    parser.add_argument('-df', '--download-following', dest='downloadfollowing', action='store_true',
                        help="PyInstaLive will check for available livestreams from users the account "
                             "used to login follows.")
    parser.add_argument('-sm', '--skip-assemble', dest='skip_assemble', action='store_true', help="PyInstaLive will not assemble the downloaded livestream files.")
    parser.add_argument('-o', '--organize', action='store_true', help="Create a folder for each user whose livestream(s) you have downloaded. The names of the folders will be their usernames. Then move the video(s) of each user into their associated folder.")

    # Workaround to 'disable' argument abbreviations
    parser.add_argument('--usernamx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--passworx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--infx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--cleax', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--downloadfollowinx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--configpatx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--confix', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--organizx', help=argparse.SUPPRESS, metavar='IGNORE')

    parser.add_argument('-cx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('-nx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('-dx', help=argparse.SUPPRESS, metavar='IGNORE')

    args, unknown_args = parser.parse_known_args()  # Parse arguments

    if validate_inputs(config, args, unknown_args):
        if not args.username and not args.password:
            pil.ig_api = auth.authenticate(username=pil.ig_user, password=pil.ig_pass)
        elif (args.username and not args.password) or (args.password and not args.username):
            logger.warn("Missing --username or --password argument.")
            logger.warn("Falling back to the configuration file values.")
            logger.separator()
            pil.ig_api = auth.authenticate(username=pil.ig_user, password=pil.ig_pass)
        elif args.username and args.password:
            pil.ig_api = auth.authenticate(username=args.username, password=args.password, force_use_login_args=True)

        if pil.ig_api:
            if pil.dl_user or pil.args.downloadfollowing:
                downloader.start()
            elif pil.dl_batchusers:
                if not helpers.command_exists("pyinstalive") and not pil.winbuild_path:
                    logger.error("PyInstaLive must be installed to use the -b argument.")
                    logger.separator()
                else:
                    dlfuncs.iterate_users(pil.dl_batchusers)
