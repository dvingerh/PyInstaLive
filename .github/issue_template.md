## Fill in this template completely. Issues not following this template will be closed and ignored.
#### Check the boxes below by filling `[ ]` with an `x` so it looks like `[x]`.
#### Use the Preview button to ensure the template is filled in correctly.
##
- [ ] I am using the latest version of PyInstaLive: 3.3.0.
- [ ] I have installed  3.6+: `YOUR VERSION HERE`
- [ ] I have read the [README](https://github.com/notcammy/pyinstalive/blob/master/README.md).
- [ ] I have read the [FAQ](https://github.com/notcammy/pyinstalive/blob/master/FAQ.md).
- [ ] I have checked all [existing issues](https://github.com/notcammy/PyInstaLive/issues?q=is%3Aissue), none of which could solve my issue.

I am using:
- [ ] Windows 10
- [ ] Windows 8.1
- [ ] Windows 8
- [ ] Windows 7
- [ ] Linux (distribution: )
- [ ] macOS (version: )
- [ ] Other (device & OS name: )
##

### To report a bug, fill in the information below.


###### Required files
Please attach the log file of the user you were trying to download (if applicable) and the `pyinstalive.default.log` log file.  
If your issue is related to assembling segment files please also include the JSON file and a zipped segment files directory.  
If any of these files exceed the Github upload size limit in size please use [WeTransfer](https://wetransfer.com/) or a similar service to upload these files.


###### PyInstaLive information 
Run ```pyinstalive --info``` and paste its output below. Don't forget to omit your **username** and **password**.

**Example:**
```bash
$ pyinstalive --info
---------------------------------------------------------------------------
[I] PYINSTALIVE (SCRIPT V3.3.0 - PYTHON V3.8.10) - 08-21-2021 03:33:23 AM
---------------------------------------------------------------------------
[I] To see all the available arguments, use the -h argument.

[I] PyInstaLive version:        3.3.0
[I] Python version:             3.8.10
[I] FFmpeg framework:           Available
[I] Login session files:        1 (johndoe.dat matches config user)
[I] CLI supports color:         Yes
[I] Command to run at start:    None
[I] Command to run at finish:   None
[I] Config file contents:

    [pyinstalive]
    username = johndoe
    password = grapefruits
    download_path = \path\to\downloads
    show_session_expires = True
    download_comments = True
    clear_temp_files = False
    skip_assemble = False
    cmd_on_started =
    cmd_on_ended =
    ffmpeg_path = 
    log_to_file = True
    use_locks = False

[I] End of PyInstaLive information screen.
---------------------------------------------------------------------------
```

###### Command used
Paste the command here that you are running. Don't forget to omit your **username** and **password**.  

**Example:** ```pyinstalive -u "johndoe" -p "grapefruits" -d "justinbieber"```

###### Behaviour
Accurately describe the issue you're experiencing with the script.

###### Steps to reproduce issue
Specify the exact steps taken to reproduce the problem. If you can't reproduce the issue try to describe the steps you've taken that eventually resulted in the issue you have experienced.

##

### To ask a question, fill in the information below.

###### Question
Describe your question here as clear as possible.
