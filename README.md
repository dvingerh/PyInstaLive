# PyInstaLive
This script enables you to record Instagram livestreams. It is based on [another script](https://github.com/taengstagram/instagram-livestream-downloader) that has now been discontinued. 

## Installation

Run the following command in command line (as administrator in Windows) / terminal:
```bash
pip install git+https://github.com/notcammy/PyInstaLive.git --process-dependency-links
```

Make sure there is a configuration file called ``pyinstalive.ini`` in the directory you want to run PyInstaLive from.

Here is an example of a valid configuration file:
```bash
[pyinstalive]
username = johndoe
password = grapefruits
save_path = C:\Instagram_Livestream_Downloads
```

#### Updating

To update PyInstaLive run the following command:

```bash
pip install git+https://github.com/notcammy/PyInstaLive.git --process-dependency-links --upgrade
```

#### Note
You need [ffmpeg](https://ffmpeg.org/download.html), [Git](https://git-scm.com/downloads) and [Python 2.x](https://www.python.org/downloads/release/python-2713/) with [Pip](https://pip.pypa.io/en/stable/installing/) installed before you can install and use this script.

## Usage
```bash
python -m pyinstalive -u "<username>" -p "<password>" -r "<live-username>"
```

Where ``<username>`` is your account's username, ``<password>`` is your password and ``<live-username>`` is the username of the user whose livestream you want to record.

#### Note
the `username` and `password` parameters are not required when you have specified these in the configuration file.

## Example
```bash
python -m pyinstalive -u "johndoe" -p "grapefruits" -r "janedoe"
```
Or (see [note](https://github.com/notcammy/PyInstaLive#note-1))
```bash
python -m pyinstalive -r "janedoe"
```

If a livestream is currently ongoing, the terminal output should be something like this:

```
PYINSTALIVE DOWNLOADER (SCRIPT v1.0)
--------------------------------------------------
[I] Login to "johndoe" OK!
[I] Checking broadcast for "janedoe"...
[I] Starting broadcast recording:
[I] Username    : janedoe
[I] MPD URL     : https://scontent-ams3-1.cdninstagram.com/hvideo-frc1/v/rNAi8avEBU6f0EgB0oLu7/live-dash/dash-abr/17870846050136409.mpd?_nc_rl=AfCS41CMvXPH2xWa&oh=43d66cf045816a1c83310da05fac0949&oe=5992E01E
[I] Viewers     : 1118 watching
[I] Airing time : 37 minutes and 20 seconds
[I] Status      : Active

[I] Recording broadcast... press [CTRL+C] to abort.

[I] Stitching downloaded files into video...
[I] Successfully stitched downloaded files!
```

## Help
If you have a bug to report please open [an issue](https://github.com/notcammy/PyInstaLive/issues) in the appropriate format:

##### - Expected behavior


##### - Actual behavior


##### - Steps to reproduce problem
