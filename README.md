## Notice
Active development for this script has ended. Issues will no longer be looked into and no more updates will be made.
**Using this script may result in your account being suspended, use at your own risk.**


# PyInstaLive
![Version 4.0.2](https://img.shields.io/badge/Version-4.0.2-orange.svg)
![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-3776ab.svg)


This Python script enables you to download ongoing Instagram livestreams as a video file.

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)


## Table of Contents
- [Quickstart](https://github.com/dvingerh/PyInstaLive#quickstart)
- [Installation](https://github.com/dvingerh/PyInstaLive#installation)
- [Usage](https://github.com/dvingerh/PyInstaLive#usage)

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Quickstart

- Install the prerequisites and then PyInstaLive.
- Run `pyinstalive` to generate a default configuration file.
- Edit the configuration file using any text editor.
- Run `pyinstalive -d "<live-username>"` to start downloading a livestream.

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Prerequisites

- [ffmpeg](https://ffmpeg.org/download.html)
- [Git](https://git-scm.com/downloads)
- [Python 3.6+](https://www.python.org/downloads/)
- [pip + setuptools](https://pip.pypa.io/en/stable/installing/)

Make sure all tools are accessible via command line (added to your PATH if on Windows, use Google).

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Installation

*Tip — To install PyInstaLive with the latest commit changes, remove the version tag from the install command.*

Run the following command in your command line (might need to be run as administrator on Windows):
```bash
pip install git+https://github.com/dvingerh/PyInstaLive.git@4.0.2
```

## Usage

Make sure there is a configuration file called ``pyinstalive.ini`` in the directory you want to run PyInstaLive from.

PyInstaLive will automatically generate a default configuration file for you to edit if one is not present already.

Here is an example of a valid configuration file:
```ini
[pyinstalive]
username = johndoe
password = grapefruit
download_path = 
ffmpeg_path = 
download_comments = True    
cmd_on_started =
cmd_on_ended =
clear_temp_files = False
use_locks = True
no_assemble = False
log_to_file = True
```

#### Example

```bash
pyinstalive -d "janedoe"
```

Below is an example of PyInstaLive's output after downloading a livestream:

```
> pyinstalive -d "janedoe"

---------------------------------------------------------------------------
[I] PYINSTALIVE (SCRIPT V4.0.2 - PYTHON V3.8.10) - 06-10-2022 05:02:02 PM
---------------------------------------------------------------------------
An existing login session file was found: johndoe.dat
Checking the validity of the saved login session.
---------------------------------------------------------------------------
Successfully logged in using account: johndoe
The login session file will expire on: 06-09-2023 at 12:41:55 PM
---------------------------------------------------------------------------
Getting livestream information for user: janedoe
---------------------------------------------------------------------------
Livestream available, starting download.
---------------------------------------------------------------------------
Downloading livestream, press [CTRL+C] to abort.
---------------------------------------------------------------------------
Airing time  : 4 minutes and 45 seconds
Status       : Active
Viewers      : 75
---------------------------------------------------------------------------
The livestream has been ended.
---------------------------------------------------------------------------
Airing time  : 6 minutes and 25 seconds
Downloaded   : 1 minutes and 21 seconds
Missing      : 5 minutes and 4 seconds
---------------------------------------------------------------------------
Waiting for background tasks to finish.
---------------------------------------------------------------------------
Saving 12 comments to text file.
Successfully saved text file: 20220610_janedoe_17905387649602356_1654873322_live.log
---------------------------------------------------------------------------
Assembling segments into video file.
Successfully saved video file: 20220610_janedoe_17905387649602356_1654873322_live.mp4
---------------------------------------------------------------------------
```
