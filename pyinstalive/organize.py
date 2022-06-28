import os
import shutil
from datetime import datetime
import time
import re

from . import logger
from . import globals

def organize_files():

    try:
        files = os.listdir(globals.config.download_path)

        not_moved = 0
        has_moved = 0

        username_regex = r'(?<=\d{8}_)(.*?)(?=_\d)'
        date_regex = r'^\d{8}'
        timestamp_regex = r'_(\d{10})_'
        raw_file_dict = {}
        new_file_dict = {}

        has_lock = any(".lock" in file for file in files)
        if has_lock:
            logger.error("The organize command cannot be used while there are lock files present.")
            return
        for file in files:
            if (file.endswith("_live.mp4") or file.endswith("_live.json")) or (os.path.isdir(file) and file.endswith("_live")):
                try:
                    if not os.path.isdir(file):
                        username = re.search(username_regex, file)[0]
                        date_ts = datetime.strptime(re.search(date_regex, file)[0], '%Y%m%d').strftime('%Y-%m-%d')
                        time_ts = time.strftime('%H-%M-%S', time.localtime(int(re.search(timestamp_regex, file)[1]))) 
                        file_ext = os.path.splitext(file)[1]
                        new_file = "{:s} {:s} {:s}{:s}".format(date_ts, time_ts, username, file_ext)
                        raw_file_dict[file] = username
                        new_file_dict[file] = new_file
                    else:
                        raw_file_dict[file] = username
                        new_file_dict[file] = file
                except TypeError as e:
                    logger.warn("Could not parse name '{:s}', skipping.".format(file))
        
        for filename, username in raw_file_dict.items():
            try:
                os.makedirs(os.path.join(globals.config.download_path, username))
            except:
                pass
            source_path = os.path.join(globals.config.download_path, filename)
            destination_path = os.path.join(globals.config.download_path, username, new_file_dict.get(filename))
            if not os.path.isfile(destination_path):
                try:
                    shutil.move(source_path, destination_path)
                    logger.info("{:s} was processed successfully.".format(filename))
                    has_moved += 1
                except OSError as oe:
                    logger.warn("Could not process {:s}: {:s}".format(filename, str(oe)))
                    not_moved += 1
            else:
                logger.binfo("Did not process {:s} because it already exists in the destination folder.".format(filename))
                not_moved += 1
        if has_moved:
            logger.separator()
        logger.info("{} {} processed.".format(has_moved if has_moved else "No", "item was" if has_moved == 1 else "items were"))
        if not_moved:
            logger.binfo("{} {} not processed.".format(not_moved, "item was" if not_moved == 1 else "items were"))
    except Exception as e:
        logger.error("Could not organize files: {:s}".format(str(e)))