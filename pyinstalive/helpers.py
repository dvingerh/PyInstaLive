import time
import subprocess
import os
import shutil
import json
import shlex
import sys

try:
    import pil
    import helpers
    import logger
    from constants import Constants
except ImportError:
    from . import pil
    from . import helpers
    from . import logger
    from .constants import Constants


def strdatetime():
    return time.strftime('%m-%d-%Y %I:%M:%S %p')


def strtime():
    return time.strftime('%I:%M:%S %p')


def strdate():
    return time.strftime('%m-%d-%Y')


def strepochtime():
    return str(int(time.time()))


def strdatetime_compat():
    return time.strftime('%Y%m%d')


def command_exists(command):
    try:
        fnull = open(os.devnull, 'w')
        subprocess.call([command], stdout=fnull, stderr=subprocess.STDOUT)
        return True
    except OSError:
        return False


def run_command(command):
    try:
        fnull = open(os.devnull, 'w')
        subprocess.Popen(shlex.split(command), stdout=fnull, stderr=sys.stdout)
        return False
    except Exception as e:
        return str(e)


def bool_str_parse(bool_str):
    if bool_str.lower() in ["true", "yes", "y", "1"]:
        return True
    elif bool_str.lower() in ["false", "no", "n", "0"]:
        return False
    else:
        return "Invalid"


def check_if_guesting():
    try:
        broadcast_guest = pil.livestream_obj.get('cobroadcasters', {})[0].get('username')
    except Exception:
        broadcast_guest = None
    print(broadcast_guest)
    if broadcast_guest and not pil.has_guest:
        logger.binfo('The livestream owner has started guesting "{}".'.format(broadcast_guest))
        pil.has_guest = broadcast_guest
    if not broadcast_guest and pil.has_guest:
        logger.binfo('The livestream owner has stopped guesting "{}".'.format(broadcast_guest))
        pil.has_guest = None



def generate_json_segments():
    while True:
        pil.livestream_obj['delay'] = (int(pil.epochtime) - pil.livestream_obj['published_time'])
        if 'initial_buffered_duration' not in pil.livestream_obj and pil.broadcast_downloader.initial_buffered_duration:
            pil.livestream_obj['initial_buffered_duration'] = pil.broadcast_downloader.initial_buffered_duration
        pil.livestream_obj['segments'] = pil.broadcast_downloader.segment_meta
        try:
            with open(pil.live_folder_path + ".json", 'w') as json_file:
                json.dump(pil.livestream_obj, json_file, indent=2)
            if not pil.broadcast_downloader.stream_id:
                pil.broadcast_downloader.stream_id = pil.livestream_obj['id']
            #check_if_guesting()
            if pil.kill_segment_thread:
                break
            else:
                time.sleep(2.5)
        except Exception as e:
            logger.warn(str(e))


def clean_download_dir():
    dir_delcount = 0
    file_delcount = 0
    error_count = 0
    lock_count = 0
    try:
        logger.info('Cleaning up temporary files and folders.')
        if Constants.PYTHON_VER[0] == "2":
            directories = (os.walk(pil.dl_path).next()[1])
            files = (os.walk(pil.dl_path).next()[2])
        else:
            directories = (os.walk(pil.dl_path).__next__()[1])
            files = (os.walk(pil.dl_path).__next__()[2])

        for directory in directories:
            if directory.endswith('_downloads'):
                if not any(filename.endswith('.lock') for filename in
                           os.listdir(os.path.join(pil.dl_path, directory))):
                    try:
                        shutil.rmtree(os.path.join(pil.dl_path, directory))
                        dir_delcount += 1
                    except Exception as e:
                        logger.error("Could not remove folder: {:s}".format(str(e)))
                        error_count += 1
                else:
                    lock_count += 1
        logger.separator()
        for file in files:
            if file.endswith('_downloads.json'):
                if not any(filename.endswith('.lock') for filename in
                           os.listdir(os.path.join(pil.dl_path))):
                    try:
                        os.remove(os.path.join(pil.dl_path, file))
                        file_delcount += 1
                    except Exception as e:
                        logger.error("Could not remove file: {:s}".format(str(e)))
                        error_count += 1
                else:
                    lock_count += 1
        if dir_delcount == 0 and file_delcount == 0 and error_count == 0 and lock_count == 0:
            logger.info('The cleanup has finished. No items were removed.')
            logger.separator()
            return
        logger.info('The cleanup has finished.')
        logger.info('Folders removed:     {:d}'.format(dir_delcount))
        logger.info('Files removed:       {:d}'.format(file_delcount))
        logger.info('Locked items:        {:d}'.format(lock_count))
        logger.info('Errors:              {:d}'.format(error_count))
        logger.separator()
    except KeyboardInterrupt as e:
        logger.separator()
        logger.warn("The cleanup has been aborted.")
        if dir_delcount == 0 and file_delcount == 0 and error_count == 0 and lock_count == 0:
            logger.info('No items were removed.')
            logger.separator()
            return
        logger.info('Folders removed:     {:d}'.format(dir_delcount))
        logger.info('Files removed:       {:d}'.format(file_delcount))
        logger.info('Locked items  :      {:d}'.format(lock_count))
        logger.info('Errors:              {:d}'.format(error_count))
        logger.separator()


def show_info():
    cookie_files = []
    cookie_from_config = ''
    try:
        for file in os.listdir(os.getcwd()):
            if file.endswith(".json"):
                with open(file) as data_file:
                    try:
                        json_data = json.load(data_file)
                        if json_data.get('created_ts'):
                            cookie_files.append(file)
                    except Exception as e:
                        pass
            if pil.ig_user == file.replace(".json", ''):
                cookie_from_config = file
    except Exception as e:
        logger.warn("Could not check for cookie files: {:s}".format(str(e)))
        logger.whiteline()
    logger.info("To see all the available arguments, use the -h argument.")
    logger.whiteline()
    logger.info("PyInstaLive version:        {:s}".format(Constants.SCRIPT_VER))
    logger.info("Python version:             {:s}".format(Constants.PYTHON_VER))
    if not command_exists("ffmpeg"):
        logger.error("FFmpeg framework:           Not found")
    else:
        logger.info("FFmpeg framework:           Available")

    if len(cookie_from_config) > 0:
        logger.info("Cookie files:               {:s} ({:s} matches config user)".format(str(len(cookie_files)),
                                                                                         cookie_from_config))
    elif len(cookie_files) > 0:
        logger.info("Cookie files:               {:s}".format(str(len(cookie_files))))
    else:
        logger.warn("Cookie files:               None found")

    logger.info("CLI supports color:         {:s}".format("No" if not logger.supports_color() else "Yes"))
    logger.info(
        "Command to run at start:    {:s}".format("None" if not pil.run_at_start else pil.run_at_start))
    logger.info(
        "Command to run at finish:   {:s}".format("None" if not pil.run_at_finish else pil.run_at_finish))

    if os.path.exists(pil.config_path):
        logger.info("Config file contents:")
        logger.whiteline()
        with open(pil.config_path) as f:
            for line in f:
                logger.plain("    {:s}".format(line.rstrip()))
    else:
        logger.error("Config file:         Not found")
    logger.whiteline()
    logger.info("End of PyInstaLive information screen.")
    logger.separator()


def new_config():
    try:
        if os.path.exists(pil.config_path):
            logger.info("A configuration file is already present:")
            logger.whiteline()
            with open(pil.config_path) as f:
                for line in f:
                    logger.plain("    {:s}".format(line.rstrip()))
            logger.whiteline()
            logger.info("To create a default config file, delete 'pyinstalive.ini' and run this script again.")
            logger.separator()
        else:
            try:
                logger.warn("Could not find configuration file, creating a default one.")
                config_file = open(pil.config_path, "w")
                config_file.write(Constants.CONFIG_TEMPLATE.format(os.getcwd()).strip())
                config_file.close()
                logger.warn("Edit the created 'pyinstalive.ini' file and run this script again.")
                logger.separator()
                return
            except Exception as e:
                logger.error("Could not create default config file: {:s}".format(str(e)))
                logger.warn("You must manually create and edit it with the following template: ")
                logger.whiteline()
                for line in Constants.CONFIG_TEMPLATE.strip().splitlines():
                    logger.plain("    {:s}".format(line.rstrip()))
                logger.whiteline()
                logger.warn("Save it as 'pyinstalive.ini' and run this script again.")
                logger.separator()
    except Exception as e:
        logger.error("An error occurred: {:s}".format(str(e)))
        logger.warn(
            "If you don't have a configuration file, manually create and edit one with the following template:")
        logger.whiteline()
        logger.plain(Constants.CONFIG_TEMPLATE)
        logger.whiteline()
        logger.warn("Save it as 'pyinstalive.ini' and run this script again.")
        logger.separator()


def create_lock_user():
    try:
        if not os.path.isfile(os.path.join(pil.dl_path, pil.dl_user + '.lock')):
            if pil.use_locks:
                open(os.path.join(pil.dl_path, pil.dl_user + '.lock'), 'a').close()
                return True
        else:
            return False
    except Exception as e:
        logger.warn("Lock file could not be created. Be careful when running multiple downloads concurrently!")
        return True


def create_lock_folder():
    try:
        if not os.path.isfile(os.path.join(pil.live_folder_path, 'folder.lock')):
            if pil.use_locks:
                open(os.path.join(pil.live_folder_path, 'folder.lock'), 'a').close()
                return True
        else:
            return False
    except Exception as e:
        logger.warn("Lock file could not be created. Be careful when running multiple downloads concurrently!")
        return True


def remove_lock():
    download_folder_lock = os.path.join(pil.dl_path, pil.dl_user + '.lock')
    temp_folder_lock = os.path.join(pil.live_folder_path, 'folder.lock')
    lock_paths = [download_folder_lock, temp_folder_lock]
    for lock in lock_paths:
        try:
            os.remove(lock)
        except Exception:
            pass


def remove_temp_folder():
    try:
        shutil.rmtree(pil.live_folder_path)
    except Exception as e:
        logger.error("Could not remove segment folder: {:s}".format(str(e)))


def download_folder_has_lockfile():
    return os.path.isfile(os.path.join(pil.dl_path, pil.dl_user + '.lock'))

def winbuild_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    elif __file__:
        return None