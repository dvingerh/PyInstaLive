# Commands


- ```-h``` or ```--help```  **—**  When this flag is passed, PyInstaLive's help message will be shown containing all available commands.

- ```-u``` or ```--username```  **—**  Instagram username to login with. Requires:  ```--password```, ```--record```.

- ```-p``` or ```--password```  **—**  Instagram password to login with. Requires:  ```--username```, ```--record```.

- ```-r``` or ```--record```  **—**  The username of the user whose livestream or replay you want to save.

- ```-i``` or ```--info```  **—**  When this flag is passed, PyInstaLive will show information such as its current version, the configuration file contents, available cookie files and more.

- ```-nr``` or ```--noreplays```  **—**  When this flag is passed, PyInstaLive will not download any available replays. Overrides the configuration file.

- ```-cl``` or ```--clean```  **—**  When this flag is passed, PyInstaLive clean the current download folder by deleting folders ending in `_downloads`. Any folders that contain a `folder.lock` file (e.g. folders for ongoing downloads) will be skipped.


# Default configuration file

```ini
[pyinstalive]
username = johndoe
password = grapefruits
save_path = 
show_cookie_expiry = true
clear_temp_files = false
save_replays = true
run_at_start =
run_at_finish =
save_comments = false

[ftp]
ftp_enabled = false
ftp_host = 
ftp_save_path = 
ftp_username = 
ftp_password = 
```

```username```  **—**  Instagram username to login with.

```password```  **—**  Instagram password to login with.

```save_path```  **—**  Path to the folder where downloaded Instagram livestreams and replays will be saved. PyInstaLive must have permission to write files to this folder. If left empty, PyInstaLive will attempt to fall back to the folder where it's being run from.

```show_cookie_expiry```  **—**  When set to True, PyInstaLive will show when the current cookie used to login will expire.

```clear_temp_files```  **—**  When set to True, PyInstaLive will delete all temporary files that were downloaded as well as the folders which contained these files. Replay folders created by PyInstaLive will not be deleted because they are used to determine if a replay has already been downloaded.

```save_replays```  **—**  When set to True, PyInstaLive will check for and download any available replays.

```run_at_start```  **—**  Command to run when PyInstaLive starts recording a livestream. Leave empty to disable. (Experimental, use at own risk.)

```run_at_finish```  **—**  Command to run when PyInstaLive finishes recording a livestream. Leave empty to disable. (Experimental, use at own risk.) 
 
```save_comments```  **—**  When set to true, PyInstaLive will try to save comments from a livestream or replay to a log file. Verified users have *(v)* next to their name. (Experimental, use at own risk.)

#

```ftp_enabled```  **—** When set to true, PyInstaLive will upload downloaded files to the configured FTP server. (Experimental, use at own risk.)

```ftp_host```  **—** Host IP or URL for the FTP server.

```ftp_save_path```  **—** FTP server save path to upload the downloaded files to.

```ftp_username```  **—** FTP username to login with.

```ftp_password```  **—** FTP password to login with.
