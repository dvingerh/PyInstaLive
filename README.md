# PyInstaLive
![Version 2.3.1](https://img.shields.io/badge/Version-2.3.1-pink.svg?style=for-the-badge)

This script enables you to download Instagram livestreams as well as any available replays. It is based on [another script](https://github.com/taengstagram/instagram-livestream-downloader) that has now been discontinued. 


## Quickstart

- [Read the notes below.](https://github.com/notcammy/PyInstaLive#notes)
- Install the prerequisites and then PyInstaLive.
- Run `pyinstalive -c` to generate a configuration file.
- Edit the configuration file using any text editor.
- Run `pyinstalive -r "<live-username>"` to start recording a livestream.


## Installation

#### Prerequisites
You need [ffmpeg](https://ffmpeg.org/download.html), [Git](https://git-scm.com/downloads) and [Python 2.7.x or 3.5>=](https://www.python.org/downloads/) with [pip](https://pip.pypa.io/en/stable/installing/) and [setuptools](https://packaging.python.org/tutorials/installing-packages/#install-pip-setuptools-and-wheel) installed before you can install and use this script. Make sure all tools are accessible via command line (added to your PATH if on Windows, use Google).

#### Installing

Run the following command in command line (as administrator in Windows) / terminal:
```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@2.3.1 --process-dependency-links
```

#### Updating

To update PyInstaLive to the latest version (currently **2.3.1**) run the following command:

```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@2.3.1 --process-dependency-links --upgrade
```

**Note**: From version 2.2.9 and up, newly generated login cookie files are now named after the username in the configuration file. If you have an existing cookie file called 'credentials.json' it is a good idea to rename it to the username it is associated with so PyInstaLive won't needlessly create a new cookie file.

#### Specific versions

If you want to install a specific version of PyInstaLive, you can specify the version tag in the install command:

```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@2.1.0 --process-dependency-links
```

Use the version number you want after the **@** symbol (e.g **2.1.0**).


## Usage
Make sure there is a configuration file called ``pyinstalive.ini`` in the directory you want to run PyInstaLive from.
You can run ```pyinstalive -c``` to automatically generate a default configuration file if one is not present.

Here is an example of a valid configuration file:
```ini
[pyinstalive]
username = johndoe
password = grapefruits
save_path = 
show_cookie_expiry = true
clear_temp_files = false
save_replays = true
```

Use the following command to run PyInstaLive:

```bash
pyinstalive -u "<username>" -p "<password>" -r "<live-username>"
```

Where ``<username>`` is your account's username, ``<password>`` is your password and ``<live-username>`` is the username of the user whose livestream or replay you want to record or save.

## Example
```bash
pyinstalive -u "johndoe" -p "grapefruits" -r "janedoe"
```
Or (see [notes](https://github.com/notcammy/PyInstaLive#notes))
```bash
pyinstalive -r "janedoe"
```

If a livestream is currently ongoing, the terminal output should be something like this:

```
----------------------------------------------------------------------
PYINSTALIVE (SCRIPT V1.0 - PYTHON V2.7.14) - 12:00:01 PM
----------------------------------------------------------------------
[I] Login to "johndoe" OK!
[I] Login cookie expiry date: 2018-01-01 at 12:00:01
[I] Checking user: 'justinbieber'
[I] Checking for ongoing livestreams...
[I] Starting livestream recording:
[I] Username    : justinbieber
[I] MPD URL     : https://scontent-ams3-1.cdninstagram.com/hvideo-frc1/v/rflSWUsyCsuqE-GLYgvW4/live-dash/dash-abr/17880993205152831.mpd?_nc_rl=AfCujc4yG9bJLHVn&oh=87c4fb94668286125f1169e4441056d2&oe=5A0E8951
[I] Viewers     : 2768 watching
[I] Airing time : 5 minutes and 10 seconds
[I] Status      : Active
----------------------------------------------------------------------
[I] Recording livestream... press [CTRL+C] to abort.

[I] Stitching downloaded files into video...
[I] Successfully stitched downloaded files.
----------------------------------------------------------------------
```


#### Notes
- You can find a list of available commands and an explanation of the configuration file [here](https://github.com/notcammy/PyInstaLive/blob/master/MOREHELP.md). You can also run `pyinstalive -h` to view all available commands. 

- The `username` and `password` parameters are not required when you have specified these in the configuration file.

- This script is also reported to work on Python 3.4.x but is not officially supported.

- If the script is ran and there are available replays as well as an ongoing Instagram livestream, only the livestream will be downloaded. Run the script again after the livestream has ended to download the available replays.


## Help
If you would like to report a bug or ask a question please [open an issue](https://github.com/notcammy/PyInstaLive/issues/new).
