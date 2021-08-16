import os
import shutil
from datetime import datetime
import time
import re

try:
    import pil
    import logger
except ImportError:
    from . import pil
    from . import logger

def organize_files():

    try:
        files = [f for f in os.listdir(pil.dl_path) if os.path.isfile(os.path.join(pil.dl_path, f)) and not f.endswith(".lock") and (f.endswith(".mp4")) or (f.endswith(".json")) or (f.endswith(".log")) and (f != "pyinstalive.default.log")]
        not_moved = 0
        has_moved = 0
        has_error = False
        username_regex = r'(?<=\d{8}_)(.*?)(?=_\d)'
        log_username_regex = r'(pyinstalive_)(.*)'
        date_regex = r'^\d{8}'
        timestamp_regex = r'_(\d{10})_'
        raw_file_dict = {}
        new_file_dict = {}

        for file in files:
            if file.endswith(".mp4") or file.endswith(".json"):
                try:
                    username = re.search(username_regex, file)[0]
                    date_ts = datetime.strptime(re.search(date_regex, file)[0], '%Y%m%d').strftime('%d-%m-%Y')
                    time_ts = time.strftime('%I-%M-%S-%p', time.localtime(int(re.search(timestamp_regex, file)[1]))) 
                    file_ext = os.path.splitext(file)[1]
                    new_file = "{:s} - {:s} {:s}{:s}".format(username, date_ts, time_ts, file_ext)
                    raw_file_dict[file] = username
                    new_file_dict[file] = new_file
                except TypeError as e:
                    logger.warn("Could not parse filename: {:s}".format(file))
                    not_moved += 1 
                    has_error = True
            elif file.endswith(".log"):
                try:
                    username = re.search(log_username_regex, file)[2]
                    username_fix = os.path.splitext(username)[0]
                    new_file = "logs-{:s}.log".format(username_fix)
                    raw_file_dict[file] = username_fix
                    new_file_dict[file] = new_file
                except TypeError as e:
                    logger.warn("Could not parse filename: {:s}".format(file))
                    not_moved += 1 
                    has_error = True
        
        for filename, username in raw_file_dict.items():
            try:
                os.makedirs(os.path.join(pil.dl_path, username))
            except:
                pass
            source_path = os.path.join(pil.dl_path, filename)
            destination_path = os.path.join(pil.dl_path, username, new_file_dict.get(filename))
            if not os.path.isfile(destination_path):
                try:
                    shutil.move(source_path, destination_path)
                    logger.info("Successfully moved and renamed: {:s}.".format(filename))
                    has_moved += 1
                except OSError as oe:
                    logger.warn("Could not move and rename {:s}: {:s}".format(filename, str(oe)))
                    not_moved += 1
            else:
                logger.warn("Could not move and rename duplicate file: {:s}".format(filename))
                not_moved += 1

        if (has_moved > 0) or (not_moved > 0 and has_error):
            logger.separator()
        if has_moved:
            logger.info("{} {} moved.".format(has_moved, "file was" if has_moved == 1 else "files were"))
        if not_moved:
            logger.binfo("{} {} not moved.".format(not_moved, "file was" if not_moved == 1 else "files were"))
        if len(files) == 0:
            logger.warn("Could not find any files to organize.")
        logger.separator()
    except Exception as e:
        logger.error("Could not organize files: {:s}".format(str(e)))