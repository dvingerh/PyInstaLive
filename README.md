# PyInstaLive
![Version ](https://img.shields.io/badge/Version-2.5.8-orange.svg?longCache=true&style=flat)

This Python script enables you to download any ongoing Instagram livestreams as well as any available replays. It is based on [another script](https://github.com/taengstagram/instagram-livestream-downloader) that has now been discontinued.

## Table of Contents
- [Features](https://github.com/notcammy/PyInstaLive#features)
- [Quickstart](https://github.com/notcammy/PyInstaLive#quickstart)
- [Installation](https://github.com/notcammy/PyInstaLive#installation)
- [Usage](https://github.com/notcammy/PyInstaLive#usage)
- [Notes](https://github.com/notcammy/PyInstaLive#notes)
- [Help](https://github.com/notcammy/PyInstaLive#help)

## Features

- Download ongoing livestreams (also detects livestreams in which the user is a guest of someone else's livestream)
- Download available replays
- Download livestream and replay comments
- Run a command when starting and/or finishing a download (Experimental)

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Quickstart

- [Read the Notes & Help sections below (important!)](https://github.com/notcammy/PyInstaLive#notes)
- Install the prerequisites and then PyInstaLive.
- Run `pyinstalive -c` to generate a configuration file.
- Edit the configuration file using any text editor.
- Run `pyinstalive -d "<live-username>"` to start downloading a livestream or replay.

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Prerequisites

#### Windows (using the executable)
- [ffmpeg](https://ffmpeg.org/download.html)
- [Universal C Runtime Update](https://support.microsoft.com/en-gb/help/2999226/update-for-universal-c-runtime-in-windows) (If not using Windows 10)

#### Linux & Windows (not using the executable)
- [ffmpeg](https://ffmpeg.org/download.html)
- [Git](https://git-scm.com/downloads)
- [Python 2.7.x or 3.5>=](https://www.python.org/downloads/)
- [pip + setuptools](https://pip.pypa.io/en/stable/installing/)

Make sure all tools are accessible via command line (added to your PATH if on Windows, use Google).

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Installation

If you run Windows you can try out the Windows build available [here](https://github.com/notcammy/PyInstaLive/releases).
In case it doesn't work or you just prefer building PyInstaLive from source follow the instructions below.

*Tip — You can easily add the executable to your PATH as well by copying it to the Windows installation folder.*

#### Installing

Run the following command in Command Prompt (might need to be run as administrator on Windows) or a terminal:
```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@2.5.8 --process-dependency-links
```

#### Updating

To update PyInstaLive to the latest version (currently **2.5.8**) run the following command:

```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@2.5.8 --process-dependency-links --upgrade
```

#### Specific versions

If you want to install a specific version of PyInstaLive when for example the newest version contains a bug, you can specify the version tag in the install command:

```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@2.2.0 --process-dependency-links
```

Use the version number you want after the **@** symbol (e.g **2.2.0**).

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Usage

Make sure there is a configuration file called ``pyinstalive.ini`` in the directory you want to run PyInstaLive from.

You can run ```pyinstalive -c``` to automatically generate a default configuration file if one is not present.

Here is an example of a valid configuration file:
```ini
[pyinstalive]
username = johndoe
password = grapefruits
save_path = 
ffmpeg_path = 
show_cookie_expiry = true
clear_temp_files = false
save_lives = true
save_replays = true
run_at_start =
run_at_finish =
save_comments = false
log_to_file = false
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

----------------------------------------------------------------------
PYINSTALIVE (SCRIPT V2.5.8 - PYTHON V3.6.3) - 06:45:30 PM
----------------------------------------------------------------------
[I] Successfully logged into user "johndoe".
[I] Cookie file expiry date: 2018-09-01 at 04:38:08 PM
----------------------------------------------------------------------
[I] Getting info for "janedoe" successful.
----------------------------------------------------------------------
[I] Checking for livestreams and replays...
----------------------------------------------------------------------
[I] Livestream found, beginning download...
----------------------------------------------------------------------
[I] Username    : janedoe
[I] Viewers     : 100 watching
[I] Airing time : 2 minutes And 10 seconds
[I] Status      : Active
[I] MPD URL     : https://scontent-amt2-1.cdninstagram.com/hvideo-prn1/v/rID1yGvO_UPlsukIhbhOx/live-dash/dash-hd/17907800311113848.mpd?_nc_rl=AfBVd51QpQOj_ImC&oh=aa8d53b4fd736c0edc29c97b411bd32b&oe=5A6FDE8B
----------------------------------------------------------------------
[I] Downloading livestream... press [CTRL+C] to abort.
----------------------------------------------------------------------
[I] The livestream has ended.
[I] Download duration : 13 minutes and 10 seconds
[I] Stream duration   : 15 minutes and 20 seconds
[I] Missing (approx.) : 2 minutes and 10 seconds
----------------------------------------------------------------------
[I] Stopping comment downloading and saving comments (if any)...
[I] Successfully saved 550 comments to logfile.
----------------------------------------------------------------------
[I] Stitching downloaded files into video...
[I] Successfully stitched downloaded files into video.
----------------------------------------------------------------------
```

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Notes
- I have not much time to extensively test the changes I make to the code, so when you do encounter a problem please [open an issue](https://github.com/notcammy/PyInstaLive/issues/new) and try using an older version of PyInstaLive in the meantime.

- Python 2 cannot save most unicode characters in comments such as emojis if it's not built from source using the `--enable-unicode=ucs4` argument. Read more about this [here](https://emoji-unicode.readthedocs.io/en/latest/python2.html). This should probably not affect pre-installed Python 2 installations on Linux-based systems such as Ubuntu or Debian.

- If the script is ran and there are available replays as well as an ongoing Instagram livestream, only the livestream will be downloaded. Run the script again after the livestream has ended to download the available replays. Alternatively you can set `save_lives` to `False` in the configuration file or pass the `--nolives` argument to skip downloading of livestreams.


## Help
You can find a list of frequently asked questions [here](https://github.com/notcammy/PyInstaLive/blob/master/FAQ.md).

You can find a list of available commands and an explanation of the configuration file [here](https://github.com/notcammy/PyInstaLive/blob/master/MOREHELP.md).

If you would like to report a bug or ask a question please [open an issue](https://github.com/notcammy/PyInstaLive/issues/new).
