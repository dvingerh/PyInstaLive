import argparse
import configparser
import os
import sys
import logging
import platform
import subprocess

try:
    import urlparse
    import pil
    import auth
    import logger
    import helpers
    import downloader
    import assembler
    import dlfuncs
    import organize
    from constants import Constants
    from comments import CommentsDownloader
except ImportError:
    from urllib.parse import urlparse
    from . import pil
    from . import auth
    from . import logger
    from . import helpers
    from . import downloader
    from . import assembler
    from . import dlfuncs
    from . import organize
    from .constants import Constants
    from .comments import CommentsDownloader

def validate_inputs(config, args, unknown_args):
    error_arr = []
    banner_shown = False
    try:
        if args.configpath:
            if os.path.isfile(args.configpath):
                pil.config_path = args.configpath
            else:
                logger.banner()
                banner_shown = True
                logger.warn("Custom config path is invalid, falling back to default path: {:s}".format(pil.config_path))
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
                logger.warn("Please use only one download method. Use -h for more information.")
                logger.separator()
                return False
        elif not args.clean and not args.info and not args.assemble and not args.downloadfollowing and not args.batchfile and not args.organize and not args.generatecomments:
            logger.banner()
            logger.error("Please use a download method. Use -h for more information.")
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
            logger.warn("The following unknown argument(s) were provided and will be ignored: ")
            logger.warn('    ' + ' '.join(unknown_args))
            logger.separator()


        pil.ig_user = config.get('pyinstalive', 'username')
        pil.ig_pass = config.get('pyinstalive', 'password')
        pil.dl_path = config.get('pyinstalive', 'download_path')
        pil.run_at_start = config.get('pyinstalive', 'run_at_start')
        pil.run_at_finish = config.get('pyinstalive', 'run_at_finish')
        pil.ffmpeg_path = config.get('pyinstalive', 'ffmpeg_path')
        pil.skip_merge = config.get('pyinstalive', 'skip_merge')
        pil.args = args
        pil.config = config
        pil.proxy = config.get('pyinstalive', 'proxy')

        if args.dlpath:
            pil.dl_path = args.dlpath

        if helpers.bool_str_parse(config.get('pyinstalive', 'show_cookie_expiry')) == "Invalid":
            pil.show_cookie_expiry = False
            error_arr.append(['show_cookie_expiry', 'False'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'show_cookie_expiry')):
            pil.show_cookie_expiry = True
        else:
            pil.show_cookie_expiry = False

        if helpers.bool_str_parse(config.get('pyinstalive', 'skip_merge')) == "Invalid":
            pil.skip_merge = False
            error_arr.append(['skip_merge', 'False'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'skip_merge')):
            pil.skip_merge = True
        else:
            pil.skip_merge = False

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

        if helpers.bool_str_parse(config.get('pyinstalive', 'do_heartbeat')) == "Invalid":
            pil.do_heartbeat = True
            error_arr.append(['do_heartbeat', 'True'])
        if helpers.bool_str_parse(config.get('pyinstalive', 'do_heartbeat')):
            pil.do_heartbeat = True
        if args.noheartbeat or not helpers.bool_str_parse(config.get('pyinstalive', 'do_heartbeat')):
            pil.do_heartbeat = False
            logger.warn("Getting livestream heartbeat is disabled, this may cause degraded performance.")
            logger.separator()

        if not args.nolives and helpers.bool_str_parse(config.get('pyinstalive', 'download_lives')) == "Invalid":
            pil.dl_lives = True
            error_arr.append(['download_lives', 'True'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'download_lives')):
            pil.dl_lives = True
        else:
            pil.dl_lives = False

        if not args.noreplays and helpers.bool_str_parse(config.get('pyinstalive', 'download_replays')) == "Invalid":
            pil.dl_replays = True
            error_arr.append(['download_replays', 'True'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'download_replays')):
            pil.dl_replays = True
        else:
            pil.dl_replays = False

        if helpers.bool_str_parse(config.get('pyinstalive', 'download_comments')) == "Invalid":
            pil.dl_comments = True
            error_arr.append(['download_comments', 'True'])
        elif helpers.bool_str_parse(config.get('pyinstalive', 'download_comments')):
            pil.dl_comments = True
        else:
            pil.dl_comments = False

        if args.nolives:
            pil.dl_lives = False

        if args.noreplays:
            pil.dl_replays = False

        if args.skip_merge:
            pil.skip_merge = True

        if not pil.dl_lives and not pil.dl_replays:
            logger.error("You have disabled both livestream and replay downloading.")
            logger.error("Please enable at least one of them and try again.")
            logger.separator()
            return False

        if pil.ffmpeg_path:
            if not os.path.isfile(pil.ffmpeg_path):
                pil.ffmpeg_path = None
                cmd = "where" if platform.system() == "Windows" else "which"
                logger.warn("Custom FFmpeg binary path is invalid, falling back to environment variable.")
            else:
                logger.binfo("Overriding FFmpeg binary path: {:s}".format(pil.ffmpeg_path))
        else:
            if not helpers.command_exists('ffmpeg') and not args.info:
                logger.error("FFmpeg framework not found, exiting.")
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
                logger.warn("Custom config path is invalid, falling back to default path: {:s}".format(pil.dl_path))
                logger.separator()

        if pil.proxy and pil.proxy != '':
            parsed_url = urlparse(pil.proxy)
            if not parsed_url.netloc or not parsed_url.scheme:
                error_arr.append(['proxy', 'None'])
                pil.proxy = None

        if error_arr:
            for error in error_arr:
                logger.warn("Invalid value for '{:s}'. Using default value: {:s}".format(error[0], error[1]))
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
        elif args.generatecomments:
            pil.gencomments_arg = args.generatecomments
            CommentsDownloader.generate_log(gen_from_arg=True)
            return False
        elif args.organize:
            organize.organize_files()
            return False

        return True
    except Exception as e:
        logger.error("An error occurred: {:s}".format(str(e)))
        logger.error("Make sure the config file and given arguments are valid and try again.")
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
                        help="The username of the user whose livestream or replay you want to save.")
    parser.add_argument('-b,', '--batch-file', dest='batchfile', type=str, required=False,
                        help="Read a text file of usernames to download livestreams or replays from.")
    parser.add_argument('-i', '--info', dest='info', action='store_true', help="View information about PyInstaLive.")
    parser.add_argument('-nr', '--no-replays', dest='noreplays', action='store_true',
                        help="When used, do not check for any available replays.")
    parser.add_argument('-nl', '--no-lives', dest='nolives', action='store_true',
                        help="When used, do not check for any available livestreams.")
    parser.add_argument('-cl', '--clean', dest='clean', action='store_true',
                        help="PyInstaLive will clean the current download folder of all leftover files.")
    parser.add_argument('-cp', '--config-path', dest='configpath', type=str, required=False,
                        help="Path to a PyInstaLive configuration file.")
    parser.add_argument('-dp', '--download-path', dest='dlpath', type=str, required=False,
                        help="Path to folder where PyInstaLive should save livestreams and replays.")
    parser.add_argument('-as', '--assemble', dest='assemble', type=str, required=False,
                        help="Path to json file required by the assembler to generate a video file from the segments.")
    parser.add_argument('-gc', '--generate-comments', dest='generatecomments', type=str, required=False,
                        help="Path to json file required to generate a comments log from a json file.")
    parser.add_argument('-df', '--download-following', dest='downloadfollowing', action='store_true',
                        help="PyInstaLive will check for available livestreams and replays from users the account "
                             "used to login follows.")
    parser.add_argument('-nhb', '--no-heartbeat', dest='noheartbeat', action='store_true', help="Disable heartbeat "
                                                                                                "check for "
                                                                                                "livestreams.")
    parser.add_argument('-sm', '--skip-merge', dest='skip_merge', action='store_true', help="PyInstaLive will not merge the downloaded livestream files.")
    parser.add_argument('-o', '--organize', action='store_true', help="Create a folder for each user whose livestream(s) you have downloaded. The names of the folders will be their usernames. Then move the video(s) of each user into their associated folder.")

    # Workaround to 'disable' argument abbreviations
    parser.add_argument('--usernamx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--passworx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--infx', help=argparse.SUPPRESS, metavar='IGNORE')
    parser.add_argument('--noreplayx', help=argparse.SUPPRESS, metavar='IGNORE')
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
            logger.warn("Missing --username or --password argument. Falling back to config file.")
            logger.separator()
            pil.ig_api = auth.authenticate(username=pil.ig_user, password=pil.ig_pass)
        elif args.username and args.password:
            pil.ig_api = auth.authenticate(username=args.username, password=args.password, force_use_login_args=True)

        if pil.ig_api:
            if pil.dl_user or pil.args.downloadfollowing:
                downloader.start()
            elif pil.dl_batchusers:
                if not helpers.command_exists("pyinstalive") and not pil.winbuild_path:
                    logger.error("PyInstaLive must be properly installed when using the -b argument.")
                    logger.separator()
                else:
                    dlfuncs.iterate_users(pil.dl_batchusers)
