import time
import os
import sys
import json
import re
import subprocess
import shlex

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
                logger.warn("Please manually create one using the following template: ")
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

def get_shared_data(html):
    match = re.search(r"window._sharedData = ({[^\n]*});", html)
    return json.loads(match.group(1))

def lock_exists():
    return os.path.isfile(os.path.join(globals.config.download_path, globals.download.download_user + '.lock'))

def lock_create():
    try:
        open(os.path.join(globals.config.download_path, globals.download.download_user + '.lock'), 'a').close()
    except Exception:
        logger.warn("Could not create lock file.")

def lock_remove():
    try:
        os.remove(os.path.join(globals.config.download_path, globals.download.download_user + '.lock'))
    except Exception:
        pass

def write_data_json():
    if not globals.download.download_stop:
        try:
            globals.download.livestream_object['segments'] = globals.download.downloader_object.segment_meta
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
        is_init = True
        if globals.download.livestream_object:
            livestream_object = globals.download.livestream_object
            is_init = False
        
        if duration_type == "airtime":
            if is_init:
                stream_started_mins, stream_started_secs = divmod((int(time.time()) - livestream_object.get("broadcast_dict").get("published_time")), 60)
            else:
                stream_started_mins, stream_started_secs = divmod((int(time.time()) - livestream_object.get("published_time")), 60)

        elif duration_type == "download":
            stream_started_mins, stream_started_secs = divmod((int(time.time()) - int(globals.download.timestamp)), 60)

        elif duration_type == "missing":
            if (int(globals.download.timestamp) - livestream_object.get("published_time")) <= 0:
                stream_started_mins, stream_started_secs = 0, 0 # Download started 'earlier' than actual broadcast, assume started at the same time instead
            else:
                if is_init:
                    stream_started_mins, stream_started_secs = divmod((int(globals.download.timestamp) - livestream_object.get("broadcast_dict").get("published_time")), 60)
                else:
                    stream_started_mins, stream_started_secs = divmod((int(globals.download.timestamp) - livestream_object.get("published_time")), 60)
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
    except Exception:
        return "Not available"

def print_durations(download_ended=False):
        logger.info('Airing time  : {}'.format(get_stream_duration("airtime")))
        if download_ended:
            logger.info('Downloaded   : {}'.format(get_stream_duration("download")))
            logger.info('Missing      : {}'.format(get_stream_duration("missing")))

def check_if_guesting():
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

def print_heartbeat(from_thread=False):
    if not globals.download.download_stop:
        if not globals.download.livestream_object:
            previous_state = globals.download.livestream_object_init.get("broadcast_dict").get("broadcast_status")
        else:
            previous_state = globals.download.livestream_object.get("broadcast_status")
        globals.download.livestream_object = api.get_heartbeat()
        if globals.config.download_comments:
            globals.comments.retrieve_comments()
        write_data_json()
        if from_thread:
            check_if_guesting()
        if not from_thread or (previous_state != globals.download.livestream_object.get("broadcast_status")):
            if from_thread:
                logger.separator()
                print_durations()
            logger.info('Status       : {}'.format(globals.download.livestream_object.get("broadcast_status").capitalize()))
            logger.info('Viewers      : {}'.format( int(globals.download.livestream_object.get("viewer_count"))))
        return globals.download.livestream_object.get('broadcast_status') not in ['available', 'interrupted']

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
        print_heartbeat(True)
        if globals.download.download_stop:
            break
        else:
            time.sleep(5)