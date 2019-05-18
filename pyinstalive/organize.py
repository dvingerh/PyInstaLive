import os
import shutil
try:
    import logger
except ImportError:
    from . import logger

def organize_videos():

    # Make a variable equal to the names of the files in the current directory.
    current_dir_files = os.listdir()

    # The downloaded livestream(s) are in MP4 format.
    video_format = ['mp4']

    # Find the MP4 files and save them in a variable called 'filenames'.
    filenames = [filename for filename in current_dir_files
        if filename.split('.')[-1] in video_format]

    if len(filenames) == 0:
        logger.error("No MP4 files in the current directory.")
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
        if not os.path.isdir(username):
            os.mkdir(username)

    # Move the videos into the folders
    for filename, username in filenames_to_usernames.items():
        shutil.move(filename, username)

    num_videos_moved = len(filenames_to_usernames.keys())
    logger.info("{} videos moved successfully.".format(num_videos_moved))