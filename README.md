## Notice
Active development for this script has ended. Issues will no longer be looked into and no more updates will be made.


# PyInstaLive
![Version 3.3.0](https://img.shields.io/badge/Version-3.3.0-orange.svg)
![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-3776ab.svg)


This Python script enables you to download ongoing Instagram livestreams as a video file.

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)


## Table of Contents
- [Quickstart](https://github.com/dvingerh/PyInstaLive#quickstart)
- [Installation](https://github.com/dvingerh/PyInstaLive#installation)
- [Usage](https://github.com/dvingerh/PyInstaLive#usage)
- [Help](https://github.com/dvingerh/PyInstaLive#help)

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Quickstart

- Install the prerequisites and then PyInstaLive.
- Run `pyinstalive` to generate a default configuration file.
- Edit the configuration file using any text editor.
- Run `pyinstalive -d "<live-username>"` to start downloading a livestream or replay.

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Prerequisites

- [ffmpeg](https://ffmpeg.org/download.html)
- [Git](https://git-scm.com/downloads)
- [Python 3.6+](https://www.python.org/downloads/)
- [pip + setuptools](https://pip.pypa.io/en/stable/installing/)

Make sure all tools are accessible via command line (added to your PATH if on Windows, use Google).

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Installation

*Tip — To install PyInstaLive with the latest commit changes, remove the version tag from the install command (e.g. **@3.3.0**).*

#### Installing

Run the following command in your command line (might need to be run as administrator on Windows):
```bash
pip install git+https://github.com/dvingerh/PyInstaLive.git@3.3.0
```

#### Updating

To update PyInstaLive to the latest version (currently **3.3.0**) run the following command:

```bash
pip install git+https://github.com/dvingerh/PyInstaLive.git@3.3.0 --upgrade
```

#### Specific versions

If you want to install a specific version of PyInstaLive when for example the newest version contains a bug, you can specify a different version tag in the install command:

```bash
pip install git+https://github.com/dvingerh/PyInstaLive.git@2.2.0
```

Use the version number you want after the **@** symbol (e.g **@2.2.0**).

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Usage

Make sure there is a configuration file called ``pyinstalive.ini`` in the directory you want to run PyInstaLive from.

PyInstaLive will automatically generate a default configuration file for you to edit if one is not present already.

Here is an example of a valid configuration file:
```ini
[pyinstalive]
username = johndoe
password = grapefruits
download_path = 
show_cookie_expiry = True
log_to_file = True
ffmpeg_path = 
run_at_start =
run_at_finish =
use_locks = True
clear_temp_files = False
proxy = 
skip_assemble = False
```

#### Example

```bash
pyinstalive -u "johndoe" -p "grapefruits" -d "janedoe"
```
You can omit the `username` and `password` arguments if you have specified these in the configuration file:
```bash
pyinstalive -d "janedoe"
```

Below is an example of PyInstaLive's output after downloading a livestream:

```
> pyinstalive -d "janedoe"

---------------------------------------------------------------------------
[I] PYINSTALIVE (SCRIPT V3.3.0 - PYTHON V3.8.10) - 08-12-2021 02:23:37 PM
---------------------------------------------------------------------------
[I] An existing login session file was found: johndoe.dat
[I] Checking the validity of the saved login session.
---------------------------------------------------------------------------
[I] Successfully logged in using account: johndoe
[I] The login session file will expire on: 08-12-2022 at 03:06:53 AM
---------------------------------------------------------------------------
[I] Successfully logged into account: johndoe
---------------------------------------------------------------------------
[I] Getting livestream info for user: janedoe
---------------------------------------------------------------------------
[I] Livestream available, starting download.
---------------------------------------------------------------------------
[I] Airing time  : 2 minutes and 38 seconds
[I] Status       : Active
[I] Viewers      : 492
---------------------------------------------------------------------------
[I] Downloading livestream, press [CTRL+C] to abort.
---------------------------------------------------------------------------
[I] The livestream has been ended by the user.
---------------------------------------------------------------------------
[I] Airing time  : 8 minutes and 46 seconds
[I] Downloaded   : 6 minutes and 8 seconds
[I] Missing      : 2 minutes and 38 seconds
---------------------------------------------------------------------------
[I] Waiting for background threads to finish.
---------------------------------------------------------------------------
[I] Generating comments text file.
---------------------------------------------------------------------------
[I] Successfully saved 59 comments.
---------------------------------------------------------------------------
[I] Assembling downloaded files into video.
---------------------------------------------------------------------------
[I] Created video: 20210812_janedoe_17931255316652921_1628771017_live.mp4
---------------------------------------------------------------------------
```

![](https://raw.githubusercontent.com/dvingerh/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)


## Help
You can find a list of frequently asked questions [here](https://github.com/dvingerh/PyInstaLive/blob/master/FAQ.md).

You can find a list of available commands and an explanation of the configuration file [here](https://github.com/dvingerh/PyInstaLive/blob/master/MOREHELP.md).

If you would like to report a bug or ask a question please [open an issue](https://github.com/dvingerh/PyInstaLive/issues/new).
