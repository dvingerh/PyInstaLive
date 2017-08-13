# PyInstaLive
This script enables you to record Instagram livestreams. It is based on [another script](https://github.com/taengstagram/instagram-livestream-downloader) that has now been discontinued.
## Usage
```bash
python cMain.py -u "<username>" -p "<password>" -r "<live-username>"
```
Where ``<username>`` is your account's username, ``<password>`` is your password and ``<live-username>`` is the username of the user whose livestream you want to record.

## Example
```bash
python cMain.py -u "johndoe" -p "grapefruits" -r "justinbieber"
```

If a livestream is currently ongoing, the terminal output should be something like this:

```
PYINSTALIVE DOWNLOADER (Script v1.0)
--------------------------------------------------
[I] Login to "johndoe" OK!
[I] Checking broadcast for "justinbieber"...
[I] Starting broadcast recording:
[I] Username    : justinbieber
[I] MPD URL     : https://scontent-ams3-1.cdninstagram.com/hvideo-frc1/v/rNAi8avEBU6f0EgB0oLu7/live-dash/dash-abr/17870846050136409.mpd?_nc_rl=AfCS41CMvXPH2xWa&oh=43d66cf045816a1c83310da05fac0949&oe=5992E01E
[I] Viewers     : 1118 watching
[I] Airing time : 37 minutes and 20 seconds
[I] Status      : Active

[I] Recording broadcast...
```

## Help
If you have a bug to report please open [an issue](https://github.com/notcammy/PyInstaLive/issues) in the appropriate format:

##### - Expected behavior


##### - Actual behavior


##### - Steps to reproduce problem
