# Commands


- ```-h``` or ```--help```  **—**  When this argument is passed, PyInstaLive's help message will be shown containing all available commands.

- ```-u``` or ```--username```  **—**  Instagram username to login with. Requires:  ```--password```, ```--download```.

- ```-p``` or ```--password```  **—**  Instagram password to login with. Requires:  ```--username```, ```--download```.

- ```-d``` or ```--download```  **—**  The username of the user whose livestream or replay you want to save (legacy).

- ```-r``` or ```--record```  **—**  The username of the user whose livestream or replay you want to save (legacy).

- ```-i``` or ```--info```  **—**  When this argument is passed, PyInstaLive will show information such as its current version, the configuration file contents, available cookie files and more.

- ```-nr``` or ```--noreplays```  **—**  When this argument is passed, PyInstaLive will not download any available replays. Overrides the configuration file.

- ```-nl``` or ```--nolives```  **—**  When this argument is passed, PyInstaLive will not download livestreams. Overrides the configuration file.

- ```-cl``` or ```--clean```  **—**  When this argument is passed, PyInstaLive clean the current download folder by deleting folders ending in `_downloads`. Any folders that contain a `folder.lock` file (e.g. folders for ongoing downloads) will be skipped.


# Default configuration file

```ini
[pyinstalive]
username = johndoe
password = grapefruits
save_path = 
show_cookie_expiry = true
clear_temp_files = false
save_lives = true
save_replays = true
run_at_start =
run_at_finish =
save_comments = false
log_to_file = false
```

```username```  **—**  Instagram username to login with.

```password```  **—**  Instagram password to login with.

```save_path```  **—**  Path to the folder where downloaded Instagram livestreams and replays will be saved. PyInstaLive must have permission to write files to this folder. If left empty, PyInstaLive will attempt to fall back to the folder where it's being run from.

```show_cookie_expiry```  **—**  When set to True, PyInstaLive will show when the current cookie used to login will expire.

```clear_temp_files```  **—**  When set to True, PyInstaLive will delete all temporary files that were downloaded as well as the folders which contained these files. Replay folders created by PyInstaLive will not be deleted because they are used to determine if a replay has already been downloaded.

```save_lives```  **—**  When set to True, PyInstaLive will download livestreams.

```save_replays```  **—**  When set to True, PyInstaLive will download any available replays.

```run_at_start```  **—**  Command to run when PyInstaLive starts downloading a livestream. Leave empty to disable. (Experimental, use at own risk.)

```run_at_finish```  **—**  Command to run when PyInstaLive finishes downloading a livestream. Leave empty to disable. (Experimental, use at own risk.) 
 
```save_comments```  **—**  When set to true, PyInstaLive will try to save comments from a livestream or replay to a log file. Verified users have *(v)* next to their name. (Experimental, use at own risk.)

```log_to_file```  **—**  When set to true, PyInstaLive will save all its console logs to a text file. The filename will be `pyinstalive_<live-username>.log` where `<live_username>` will be the username of the Instagram user whose livestream or replay you want to download. If no username was given to download (e.g when running `pyinstalive --clean`) the file will simply be named `pyinstalive_log.log`.