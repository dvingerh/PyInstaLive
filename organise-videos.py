import os
import shutil

# Find the files in the current directory.
current_dir_files = os.listdir()

# Find the path of the current directory.
current_dir_path = os.getcwd()

# The Instagram videos are in MP4 format.
video_format = ['mp4']

# Find the MP4 files and save them in a variable called 'filenames'.
filenames = [filename for filename in current_dir_files if filename.split('.')[-1] in video_format]

# We want a dictionary where the filenames are the keys and the usernames are the values.
filenames_to_usernames = {}

# Populate the dictionary by going through each filename and removing the undesired characters, leaving just the usernames.
for filename in filenames:
    filename_parts = filename.split('_')[1:-3]
    usernames = '_'.join(filename_parts)
    filenames_to_usernames[filename] = usernames

# The usernames are the values of the filenames_to_usernames dictionary.
usernames = filenames_to_usernames.values()

# Make a folder for each username.
for username in usernames:
    if not os.path.isdir(username):
        os.mkdir(username)

# We want a dictionary where the usernames are the keys and the associated folder paths are the keys.
username_to_folder = {}

# Populate the dictionary.
for username in usernames:
    folder_paths = current_dir_path + "\\" + username
    username_to_folder[username] = folder_paths

# Move the videos into the folders
for filename, username in filenames_to_usernames.items():
    shutil.move(filename, username)
    # Can also do os.rename(filename, '{}/{}'.format(username, filename))

num_videos_moved = len(filenames_to_usernames.keys())
print("{} videos moved successfully.".format(num_videos_moved))