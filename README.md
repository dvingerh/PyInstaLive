# PyInstaLive
![Version 3.2.0](https://img.shields.io/badge/Version-3.2.0-orange.svg)
![Python 2.7, 3.5](https://img.shields.io/badge/Python-2.7%2C%203.5%2B-3776ab.svg)

[![Support me!](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/dvingerh)


This Python script enables you to download any ongoing Instagram livestreams as well as any available replays. It is based on [another script](https://github.com/taengstagram/instagram-livestream-downloader) that has now been discontinued.

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)


## Table of Contents
- [Features](https://github.com/notcammy/PyInstaLive#features)
- [Quickstart](https://github.com/notcammy/PyInstaLive#quickstart)
- [Installation](https://github.com/notcammy/PyInstaLive#installation)
- [Usage](https://github.com/notcammy/PyInstaLive#usage)
- [Notes](https://github.com/notcammy/PyInstaLive#notes)
- [Help](https://github.com/notcammy/PyInstaLive#help)

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Main Features

PyInstaLive is capable of downloading:
- Ongoing livestreams (also detects livestreams where the specified user is being guested).
- Saved replays.
- Livestream and replay comments.
- Available livestreams and replays from your following user feed, concurrently.

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Quickstart

- [Read the Notes & Help sections below (important!)](https://github.com/notcammy/PyInstaLive#notes)
- Install the prerequisites and then PyInstaLive.
- Run `pyinstalive` to generate a default configuration file.
- Edit the configuration file using any text editor.
- Run `pyinstalive -d "<live-username>"` to start downloading a livestream or replay.

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Prerequisites

- [ffmpeg](https://ffmpeg.org/download.html)
- [Git](https://git-scm.com/downloads)
- [Python 2.7.x or 3.5>=](https://www.python.org/downloads/)
- [pip + setuptools](https://pip.pypa.io/en/stable/installing/)

Make sure all tools are accessible via command line (added to your PATH if on Windows, use Google).

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Installation

*Tip — To install PyInstaLive with the latest commit changes, remove the version tag from the install command (e.g. **@3.2.0**).*

#### Installing

Run the following command in your command line (might need to be run as administrator on Windows):
```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@3.2.0
```

#### Updating

To update PyInstaLive to the latest version (currently **3.2.0**) run the following command:

```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@3.2.0 --upgrade
```

#### Specific versions

If you want to install a specific version of PyInstaLive when for example the newest version contains a bug, you can specify a different version tag in the install command:

```bash
pip install git+https://github.com/notcammy/PyInstaLive.git@2.2.0
```

Use the version number you want after the **@** symbol (e.g **@2.2.0**).

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Usage

Make sure there is a configuration file called ``pyinstalive.ini`` in the directory you want to run PyInstaLive from.

PyInstaLive will automatically generate a default configuration file for you to edit if one is not present already.

Here is an example of a valid configuration file:
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
[I] PYINSTALIVE (SCRIPT V3.2.0 - PYTHON V3.6.3) - 01-02-2019 06:56:29 PM
---------------------------------------------------------------------------
[I] Successfully logged into account: johndoe
---------------------------------------------------------------------------
[I] Getting info for 'janedoe' successful.
---------------------------------------------------------------------------
[I] Livestream available, starting download.
---------------------------------------------------------------------------
[I] Username    : janedoe
[I] Viewers     : 335 watching
[I] Airing time : 2 minutes and 8 seconds
[I] Status      : Active
---------------------------------------------------------------------------
[I] Downloading livestream, press [CTRL+C] to abort.
---------------------------------------------------------------------------
[I] The livestream has been ended by the user.
---------------------------------------------------------------------------
[I] Airtime duration  : 3 minutes and 13 seconds
[I] Download duration : 1 minutes and 7 seconds
[I] Missing (approx.) : 2 minutes and 6 seconds
---------------------------------------------------------------------------
[I] Waiting for comment downloader to finish.
[I] Successfully saved 19 comments.
---------------------------------------------------------------------------
[I] Merging downloaded files into video.
[I] Successfully merged downloaded files into video.
---------------------------------------------------------------------------
[I] There are no available replays.
---------------------------------------------------------------------------
```

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)

## Notes
- I have not much time to extensively test the changes I make to the code, so when you do encounter a problem please [open an issue](https://github.com/notcammy/PyInstaLive/issues/new) and try using an older version of PyInstaLive in the meantime.

- Python 2 cannot save most unicode characters in comments such as emojis if it's not built from source using the `--enable-unicode=ucs4` argument. Read more about this [here](https://emoji-unicode.readthedocs.io/en/latest/python2.html). This should probably not affect pre-installed Python 2 installations on Linux-based systems such as Ubuntu or Debian.

![](https://raw.githubusercontent.com/notcammy/PyInstaLive/5907fc866446d5f426389a5198560075848d770e/.github/spacer.png)


## Help
You can find a list of frequently asked questions [here](https://github.com/notcammy/PyInstaLive/blob/master/FAQ.md).

You can find a list of available commands and an explanation of the configuration file [here](https://github.com/notcammy/PyInstaLive/blob/master/MOREHELP.md).

If you would like to report a bug or ask a question please [open an issue](https://github.com/notcammy/PyInstaLive/issues/new).
