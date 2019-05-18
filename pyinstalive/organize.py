import os
import shutil
try:
    import pil
    import logger
except ImportError:
    from . import pil
    from . import logger

def organize_videos():

    try:
        # Make a variable equal to the names of the files in the current directory.
        current_dir_files = os.listdir(pil.dl_path)

        # Count the amount of files moved and not moved because they already exist etc.
        not_moved = 0
        has_moved = 0

        # The downloaded livestream(s) are in MP4 format.
        video_format = ['mp4']

        # Find the MP4 files and save them in a variable called 'filenames'.
        filenames = [os.path.join(pil.dl_path, filename) for filename in current_dir_files
            if filename.split('.')[-1] in video_format]

        if len(filenames) == 0:
            logger.binfo("No files were found to organize.")
            logger.separator()
            return

        # We want a dictionary where the filenames are the keys
        # and the usernames are the values.
        filenames_to_usernames = {}

        # Populate the dictionary by going through each filename and removing the
        # undesired characters, leaving just the usernames.
        for filename in filenames:
            filename_parts = filename.split('_')[1:-3]
            usernames = '_'.join(filename_parts)
            filenames_to_usernames[filename] = usernames
            
        # The usernames are the values of the filenames_to_usernames dictionary.
        usernames = set(filenames_to_usernames.values())

        # Make a folder for each username.
        for username in usernames:
            username_path = os.path.join(pil.dl_path, username)
            if not os.path.isdir(username_path):
                os.mkdir(username_path)

        # Move the videos into the folders
        for filename, username in filenames_to_usernames.items():
            filename_base = os.path.basename(filename)
            destination_path = os.path.join(pil.dl_path, username, filename_base)
            if not os.path.isfile(destination_path):
                try:
                    shutil.move(filename, destination_path)
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