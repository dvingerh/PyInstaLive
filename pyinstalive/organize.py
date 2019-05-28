import os
import shutil
from datetime import datetime
import time
try:
    import pil
    import logger
except ImportError:
    from . import pil
    from . import logger

def organize_videos():

    try:
        # Make a variable equal to the names of the files in the current directory.
        download_path_files = os.listdir(pil.dl_path)

        # Count the amount of files moved and not moved because they already exist etc.
        not_moved = 0
        has_moved = 0

        # The downloaded livestream(s) are in MP4 format.
        video_format = ['mp4']

        # Find the MP4 files and save them in a variable called 'filenames'.
        filenames = [filename for filename in download_path_files
            if filename.split('.')[-1] in video_format]
        
        if len(filenames) == 0:
            logger.binfo("No files were found to organize.")
            logger.separator()
            return

        for filename in filenames:
            # Split the filenames into parts.
            filename_parts = filename.split('_')

            # Get the date from the filename.
            date = datetime.strptime(filename_parts[0], '%Y%m%d').strftime('%d-%m-%Y')

            # Get the username from the filename. 
            username = '_'.join(filename_parts[1:-3])

            # Get the time from the unix timestamp.
            time_from_unix_timestamp = time.strftime('%I.%M%p', time.localtime(int(filename_parts[-2])))

            # # Remove the leading zero from single-digit hours.
            if float(time_from_unix_timestamp[0:2]) < 10:
                time_from_unix_timestamp = time_from_unix_timestamp[1:]

            # Get the last part of the filename ("live.mp4" or "replay.mp4").
            live_or_replay = filename_parts[-1]
            
            # The path of each original filename is as follows:
            old_filename_path = os.path.join(pil.dl_path, filename)

            # We want to change the format of each filename to:
            new_filename_format = date + " " + username + " [" + time_from_unix_timestamp + "] " + live_or_replay

            # The path of each new filename is as follows:
            new_filename_path = os.path.join(pil.dl_path, new_filename_format)

            # Change the filenames.
            os.rename(old_filename_path, new_filename_path)

        # Now that the files have been renamed, we need to rescan the files in the directory.
        download_path_files = os.listdir(pil.dl_path)

        new_filenames = [filename for filename in download_path_files if filename.split('.')[-1] in video_format]
        
        # We want a dictionary where the filenames are the keys
        # and the usernames are the values.
        filenames_to_usernames = {}

        # Populate the dictionary with a loop.
        for filename in new_filenames:
            # Split the filenames into parts so we get just the usernames:
            filename_parts = filename.split()
            # This is how to get the usernames from the split filenames:
            username = filename_parts[1]
            # Filename = key and username = value:
            filenames_to_usernames[filename] = username
    
        # We only want one folder for each username, so convert the list into a set to remove duplicates.
        usernames = set(filenames_to_usernames.values())

        # Make a folder for each username.
        for username in usernames:
            username_path = os.path.join(pil.dl_path, username)
            if not os.path.isdir(username_path):
                os.mkdir(username_path)

        # Move the videos into the folders
        for filename, username in filenames_to_usernames.items():
            filename_base = os.path.basename(filename)
            source_path = os.path.join(pil.dl_path, filename)
            destination_path = os.path.join(pil.dl_path, username, filename_base)
            if not os.path.isfile(destination_path):
                try:
                    shutil.move(source_path, destination_path)
                    logger.info("Moved '{:s}' successfully.".format(filename_base))
                    has_moved += 1
                except OSError as oe:
                    logger.warn("Could not move {:s}: {:s}".format(filename_base, str(oe)))
                    not_moved += 1
            else:
                logger.binfo("Did not move '{:s}' because it already exists.".format(filename_base))
                not_moved += 1

        logger.separator()
        logger.info("{} {} moved.".format(has_moved, "file was" if has_moved == 1 else "files were"))
        if not_moved:
            logger.binfo("{} {} not moved.".format(not_moved, "file was" if not_moved == 1 else "files were"))
        logger.separator()
    except Exception as e:
        logger.error("Could not organize files: {:s}".format(str(e)))