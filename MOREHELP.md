# Commands


- ```-h``` or ```--help```  **—**  PyInstaLive's help message will be shown containing all available commands.

- ```-u``` or ```--username```  **—**  Instagram username to login with. Requires:  ```--password```, ```--download```.

- ```-p``` or ```--password```  **—**  Instagram password to login with. Requires:  ```--username```, ```--download```.

- ```-d``` or ```--download```  **—**  The username or user Id of the user whose livestream or replay you want to save.

- ```-i``` or ```--info```  **—**  PyInstaLive will show information such as its current version, the configuration file contents, available cookie files and other relevant information.

- ```-nr``` or ```--no-replays```  **—**  PyInstaLive will not download any available replays. Overrides the configuration file value.

- ```-nl``` or ```--no-lives```  **—**  PyInstaLive will not download livestreams. Overrides the configuration file value.

- ```-cl``` or ```--clean```  **—**  PyInstaLive clean the current download folder by deleting folders ending in `_downloads`. Any folders that contain a `folder.lock` file (e.g. folders for ongoing downloads) will be skipped.

- ```-df``` or ```--download-following```  **—**  PyInstaLive will check if any users from your following list have any available livestreams or replays and start a daemon process running PyInstaLive in the background for those that do. You cannot cancel the launched processes or start them with any extra arguments. It's recommended to enable ```log_to_file``` when using this argument. (Experimental, use at own risk.)

- ```-cp``` or ```--config-path```  **—**  Passing this argument along with a valid path to a different configuration file will override the default path used by PyInstaLive (the current directory you are executing the script in).

- ```-dp``` or ```--download-path```  **—**  Passing this argument along with a valid path to a different folder will override the path specified in the configuration file.

- ```-as``` or ```--assemble```  **—** PyInstaLive will try to generate a video file from a given segments file directory or its accompanied JSON file (when available). 

- ```-b``` or ```--batch-file```  **—** PyInstaLive will check the users inside a text file for any available livestreams or replays.

- ```-nhb``` or ```--no-heartbeat```  **—** Passing this argument means no livestream heartbeat checks will be conducted, and the logged in user will not show up as a viewer during the livestream. May cause degraded performance.

- ```-o``` or ```--organize```  **—** Passing this argument will create a folder for each user whose livestream(s) you have downloaded. The names of the folders will be their usernames. It will then move the video and log files of each user into their associated folder and rename the files to a more friendly format. Example filename: ```19-04-2020 06-02-10-PM johndoe (replay).mp4```. Temporary file segment folders will not be moved.

- ```-sm``` or ```--skip-merge```  **—** PyInstaLive will not merge any download livestream files when this argument is used.

# Default configuration file

```ini
[pyinstalive]
username = johndoe
password = grapefruits
download_path = 
download_lives = True
download_replays = True
download_comments = true
show_cookie_expiry = True
log_to_file = True
ffmpeg_path = 
run_at_start =
run_at_finish =
use_locks = True
clear_temp_files = False
do_heartbeat = True
proxy = 
verbose = False
skip_merge = False
```

```username```  **—**  Instagram username to login with.

```password```  **—**  Instagram password to login with.

```download_path```  **—**  Path to the folder where downloaded Instagram livestreams and replays will be saved. PyInstaLive must have permission to write files to this folder. If left empty, PyInstaLive will attempt to fall back to the folder where it's being run from.

```download_lives```  **—**  When set to True, PyInstaLive will download livestreams.

```download_replays```  **—**  When set to True, PyInstaLive will download any available replays.

```download_comments```  **—**  When set to true, PyInstaLive will try to download comments from a livestream or replay to a log file. Verified users have *(v)* next to their name.

```show_cookie_expiry```  **—**  When set to True, PyInstaLive will show when the current cookie used to login will expire.

```log_to_file```  **—**  When set to true, PyInstaLive will save all its console logs to a text file. The filename will be `pyinstalive_<live-username>.log` where `<live_username>` will be the username of the Instagram user whose livestream or replay you want to download. If no username was given to download (e.g when running `pyinstalive --clean`) the file will be named `pyinstalive.default.log`.

```ffmpeg_path```  **—**  User-defined path to the FFmpeg binary (e.g. `C:\Users\Username\Desktop\ffmpeg.exe`). If left empty, PyInstaLive will fall back to the system's environment variable.

```run_at_start```  **—**  Command to run when PyInstaLive starts downloading a livestream. Leave empty to disable. (Experimental feature)

```run_at_finish```  **—**  Command to run when PyInstaLive finishes downloading a livestream. Leave empty to disable. (Experimental feature) 

```use_locks```  **—**  When set to true, PyInstaLive will create several .lock files to prevent duplicate downloads from starting for the same user if you are running PyInstaLive using some form of automation such as batch/shell loops.

```clear_temp_files```  **—**  When set to True, PyInstaLive will delete all temporary files that were downloaded as well as the folders which contained these files. Replay folders created by PyInstaLive will not be deleted because they are used to determine if a replay has already been downloaded.

```do_heartbeat```  **—**  When set to True, PyInstaLive will check the livestream's active status. If set to False no checks will be conducted, and the logged in user will not show up as a viewer during the livestream. May cause degraded performance.

```proxy```  **—**  When set, PyInstaLive will use the specified HTTP proxy. The format should be similar to http://user:pass@proxy.com:12345


