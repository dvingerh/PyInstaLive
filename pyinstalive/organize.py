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
        files = [f for f in os.listdir(pil.dl_path) if os.path.isfile(os.path.join(pil.dl_path, f)) and not f.endswith(".lock")]

        not_moved = 0
        has_moved = 0

        username_regex = r'(?<=\d{8}_)(.*?)(?=_\d)'
        date_regex = r'^\d{8}'
        timestamp_regex = r'_(\d{10})_'
        type_regex = r'(live|replay)'
        raw_file_dict = {}
        new_file_dict = {}

        for file in files:
            try:
                username = re.search(username_regex, file)[0]
                date_ts = datetime.strptime(re.search(date_regex, file)[0], '%Y%m%d').strftime('%d-%m-%Y')
                time_ts = time.strftime('%I-%M-%S-%p', time.localtime(int(re.search(timestamp_regex, file)[1]))) 
                file_ext = os.path.splitext(file)[1]
                file_type = re.search(type_regex, file)[0]
                json_type = ""
                if file.endswith("_downloads.json"):
                    json_type = " downloads"
                elif file.endswith("_comments.json"):
                    json_type = " comments"
                new_file = "{:s} {:s} {:s} ({:s}){:s}{:s}".format(date_ts, time_ts, username, file_type, json_type, file_ext)
                raw_file_dict[file] = username
                new_file_dict[file] = new_file
            except TypeError as e:
                logger.warn("Could not parse filename '{:s}', skipping.".format(file))
        
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
                    logger.info("Moved and renamed '{:s}' successfully.".format(filename))
                    has_moved += 1
                except OSError as oe:
                    logger.warn("Could not move and rename {:s}: {:s}".format(filename, str(oe)))
                    not_moved += 1
            else:
                logger.binfo("Did not move and rename '{:s}' because it already exists.".format(filename))
                not_moved += 1

        logger.separator()
        logger.info("{} {} moved.".format(has_moved, "file was" if has_moved == 1 else "files were"))
        if not_moved:
            logger.binfo("{} {} not moved.".format(not_moved, "file was" if not_moved == 1 else "files were"))
        logger.separator()
    except Exception as e:
        logger.error("Could not organize files: {:s}".format(str(e)))