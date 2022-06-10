import time
import os
import json
import re
import subprocess
import shlex
import shutil

from . import globals
from . import logger
from . import api
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

def new_config():
    try:
        if os.path.exists(globals.config.config_path):
            logger.info("A configuration file is already present:")
            logger.whiteline()
            with open(globals.config.config_path) as f:
                for line in f:
                    logger.plain("    {:s}".format(line.rstrip()))
            logger.whiteline()
            logger.info("To create a default configuration file, delete the existing file and run PyInstaLive again.")
            logger.separator()
        else:
            try:
                logger.warn("Could not find configuration file, creating a default one.")
                config_file = open(globals.config.config_path, "w")
                config_file.write(Constants.CONFIG_TEMPLATE.format(os.getcwd()).strip())
                config_file.close()
                logger.info("A new configuration file has been created.")
                logger.separator()
                return
            except Exception as e:
                logger.error("Could not create default configuration file: {:s}".format(str(e)))
                logger.warn("Manually create one using the following template: ")
                logger.whiteline()
                for line in Constants.CONFIG_TEMPLATE.strip().splitlines():
                    logger.plain("    {}".format(line.rstrip()))
                logger.whiteline()
                logger.warn("Save it as 'pyinstalive.ini' and run this script again.")
                logger.separator()
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        logger.warn("If configuration file exists, manually create one using the following template:")
        logger.whiteline()
        logger.plain(Constants.CONFIG_TEMPLATE)
        logger.whiteline()
        logger.warn("Save it as 'pyinstalive.ini' and run this script again.")
        logger.separator()

def string_escape(s, encoding='utf-8'):
    return (s.encode('latin1')
             .decode('unicode-escape')
             .encode('latin1')
             .decode(encoding))

def get_shared_data(data):
    match = re.search(r"window._sharedData = ({[^\n]*});", data)
    match_str = None
    if match:
        match_str = match.group(1)
        return json.loads(match_str).get("config")
    else:
        match = re.search(r"\"raw\":\"({[^\n]*\\\"})", data)
        if match:
            match_str = string_escape(match.group(1))
            return json.loads(match_str)

def lock_exists():
    return os.path.isfile(os.path.join(globals.config.download_path, globals.download.download_user + '.lock'))

def lock_create(lock_type="user"):
    try:
        if lock_type == "user":
            open(os.path.join(globals.config.download_path, globals.download.download_user + '.lock'), 'a').close()
        elif lock_type == "folder":
            open(os.path.join(globals.download.segments_path, globals.download.download_user + ".lock"), 'a').close()
    except Exception:
        logger.warn("Could not create lock file.")

def lock_remove():
    try:
        os.remove(os.path.join(globals.config.download_path, globals.download.download_user + '.lock'))
        os.remove(os.path.join(globals.download.segments_path, globals.download.download_user + ".lock"))
    except Exception:
        pass

def write_data_json():
    if not globals.download.download_stop:
        try:
            globals.download.livestream_object['segments'] = globals.download.downloader_object.segment_meta
            if globals.comments:
                globals.download.livestream_object['comments'] = globals.comments.comments
            try:
                with open(globals.download.data_json_path, 'w') as json_file:
                    json.dump(globals.download.livestream_object, json_file, indent=2)
            except Exception as e:
                logger.warn(str(e))
        except Exception as e:
            logger.warn(str(e))

def get_stream_duration(duration_type="airtime"):
    try:
        livestream_object = globals.download.livestream_object_init
        buffer = int(globals.download.downloader_object.initial_buffered_duration)
        if duration_type == "airtime":
            stream_started_mins, stream_started_secs = divmod((int(time.time()) - livestream_object.get("published_time") + buffer), 60)

        elif duration_type == "download":
            stream_started_mins, stream_started_secs = divmod((int(time.time()) - int(globals.download.timestamp)), 60)

        elif duration_type == "missing":
            sum = (int(globals.download.timestamp) - livestream_object.get("published_time") + buffer)
            if sum <= 0:
                stream_started_mins, stream_started_secs = 0, 0 
            else:
                stream_started_mins, stream_started_secs = divmod((int(globals.download.timestamp) - livestream_object.get("published_time") + buffer), 60)
        else:
            stream_started_mins, stream_started_secs = 0, 0 

        if stream_started_mins < 0:
            stream_started_mins = 0
        if stream_started_secs < 0:
            stream_started_secs = 0

        stream_duration_str = '{} minutes'.format(stream_started_mins)
        if stream_started_secs:
            stream_duration_str += ' and {} seconds'.format(stream_started_secs)
        return stream_duration_str
    except Exception as e:
        print(str(e))
        return "?"

def print_durations(download_ended=False):
        logger.info('Airing time  : {}'.format(get_stream_duration("airtime")))
        if download_ended:
            logger.info('Downloaded   : {}'.format(get_stream_duration("download")))
            logger.info('Missing      : {}'.format(get_stream_duration("missing")))


def command_exists(command):
    try:
        fnull = open(os.devnull, 'w')
        subprocess.call([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def run_command(command):
    try:
        fnull = open(os.devnull, 'w')
        subprocess.Popen(shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return False
    except Exception as e:
        return str(e)


def handle_tasks_worker():
    while True:
        globals.download.update_stream_data(from_thread=True)
        lock_create(lock_type="folder")
        if globals.download.download_stop:
            break
        else:
            time.sleep(3)

def clean_download_dir():
    dir_delcount = 0
    file_delcount = 0
    error_count = 0
    lock_count = 0
    try:
        logger.info('Cleaning up temporary files and folders.')
        directories = os.walk(globals.config.download_path).__next__()[1]
        files = os.walk(globals.config.download_path).__next__()[2]

        for directory in directories:
            if directory.endswith('_live'):
                if not any(filename.endswith('.lock')  for filename in
                           os.listdir(os.path.join(globals.config.download_path, directory))):
                    try:
                        shutil.rmtree(os.path.join(globals.config.download_path, directory))
                        dir_delcount += 1
                    except Exception as e:
                        logger.error("Could not remove folder: {:s}".format(str(e)))
                        error_count += 1
                else:
                    lock_count += 1
        logger.separator()
        for file in files:
            if file.endswith('_live.json'):
                if not any(filename.endswith('.lock') for filename in
                           os.listdir(os.path.join(globals.config.download_path))):
                    try:
                        os.remove(os.path.join(globals.config.download_path, file))
                        file_delcount += 1
                    except Exception as e:
                        logger.error("Could not remove file: {:s}".format(str(e)))
                        error_count += 1
                else:
                    lock_count += 1
        if dir_delcount == 0 and file_delcount == 0 and error_count == 0 and lock_count == 0:
            logger.info('The cleanup has finished. No items were removed.')
            return
        logger.info('The cleanup has finished.')
        logger.info('Folders removed:     {:d}'.format(dir_delcount))
        logger.info('Files removed:       {:d}'.format(file_delcount))
        logger.info('Locked items:        {:d}'.format(lock_count))
        logger.info('Errors:              {:d}'.format(error_count))
    except KeyboardInterrupt as e:
        logger.separator()
        logger.warn("The process was aborted by the user.")
        if dir_delcount == 0 and file_delcount == 0 and error_count == 0 and lock_count == 0:
            logger.info('No items were removed.')
            return
        logger.info('Folders removed:     {:d}'.format(dir_delcount))
        logger.info('Files removed:       {:d}'.format(file_delcount))
        logger.info('Locked items:        {:d}'.format(lock_count))
        logger.info('Errors:              {:d}'.format(error_count))

def show_info():
    session_files = []
    session_from_config = ''
    try:
        for file in os.listdir(os.getcwd()):
            if file.endswith(".dat"):
                session_files.append(file)
            if globals.config.username == file.replace(".dat", ''):
                session_from_config = file
    except Exception as e:
        logger.warn("Could not check for login session files: {:s}".format(str(e)))
        logger.whiteline()
    logger.info("To see all the available arguments, use the -h argument.")
    logger.whiteline()
    logger.info("PyInstaLive version:        {:s}".format(Constants.SCRIPT_VERSION))
    logger.info("Python version:             {:s}".format(Constants.PYTHON_VERSION))
    if not command_exists("ffmpeg"):
        logger.error("FFmpeg framework:           Not found")
    else:
        logger.info("FFmpeg framework:           Available")

    if len(session_from_config) > 0:
        logger.info("Login session files:        {:s} ({:s} matches configuration username)".format(str(len(session_files)),
                                                                                         session_from_config))
    elif len(session_files) > 0:
        logger.info("Login session files:               {:s}".format(str(len(session_files))))
    else:
        logger.warn("Login session files:               None found")

    logger.info("CLI supports color:         {:s}".format("No" if not logger.supports_color() else "Yes"))

    if os.path.exists(globals.config.config_path):
        logger.whiteline()
        logger.info("Configuration file contents:")
        logger.whiteline()
        with open(globals.config.config_path) as f:
            for line in f:
                logger.plain("    {:s}".format(line.rstrip()))
    else:
        logger.error("Configuration file:         Not found")
    logger.whiteline()
    logger.info("End of PyInstaLive information screen.")
