# Commands


- ```-h``` or ```--help```  **—**  Show PyInstaLive's help message containing all available arguments.

- ```-u``` or ```--username```  **—**  Instagram username to login with. Requires:  ```--password```, ```--record```.

- ```-p``` or ```--password```  **—**  Instagram password to login with. Requires:  ```--username```, ```--record```.

- ```-r``` or ```--record```  **—**  The username of the user whose livestream or replay you want to save.

- ```-i``` or ```--info```  **—**  View information related to PyInstaLive such as its current version, the configuration file contents, available cookie files and more.

- ```-c``` or ```--config```  **—**  Create a default configuration file if it doesn't exist. If there is already a configuration file present, it'll show you its contents instead.


# Configuration file

```ini
[pyinstalive]
username = johndoe
password = grapefruits
save_path = 
show_cookie_expiry = true
clear_temp_files = false
save_replays = true
```

```username```  **—**  Instagram username to login with.

```password```  **—**  Instagram password to login with.

```save_path```  **—**  Path to the folder where downloaded Instagram livestreams and replays will be saved. (Requires write permissions)

```show_cookie_expiry```  **—**  When set to True, PyInstaLive will show when the current cookie used to login will expire.

```clear_temp_files```  **—**  When set to True, PyInstaLive will delete all temporary files that were downloaded. Folders created by PyInstaLive will not be deleted.

```save_replays```  **—**  When set to True, PyInstaLive will check for and download any available replays.
