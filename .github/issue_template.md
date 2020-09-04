## Fill in this template completely. Issues not following this template will be closed and ignored.
#### Check the boxes below by filling `[ ]` with an `x` so it looks like `[x]`.
#### Use the Preview button to ensure the template is filled in correctly.
##
- [ ] I am using the latest version of PyInstaLive: 3.2.4.
- [ ] I have installed either Python 2.7.x or 3.5+: `YOUR VERSION HERE`
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
[I] PYINSTALIVE (SCRIPT V3.2.4 - PYTHON V3.6.3) - 01-02-2019 07:00:17 PM
---------------------------------------------------------------------------
[I] To see all the available arguments, use the -h argument.

[I] PyInstaLive version:        3.2.4
[I] Python version:             3.6.3
[I] FFmpeg framework:           Available
[I] Cookie files:               2 (johndoe.json matches config user)
[I] CLI supports color:         Yes
[I] Command to run at start:    None
[I] Command to run at finish:   None
[I] Config file contents:

    [pyinstalive]
    username = *removed*
    password = *removed*
    download_path = \path\to\downloads
    download_lives = True
    download_replays = True
    download_comments = True
    show_cookie_expiry = False
    ffmpeg_path =
    log_to_file = True
    run_at_start =
    run_at_finish =
    use_locks = True
    clear_temp_files = False

[I] End of PyInstaLive information screen.
---------------------------------------------------------------------------
```

###### Command used
Paste the command here that you are running. Don't forget to omit your **username** and **password**.  

**Example:** ```pyinstalive -u "johndoe" -p "grapefruits" -d "justinbieber"```

###### Behavior
Accurately describe the issue you're experiencing with the script.

###### Steps to reproduce issue
Specify the exact steps taken to reproduce the problem. If you can't reproduce the issue try to describe the steps you've taken that eventually resulted in the issue you have experienced.

##

### To ask a question, fill in the information below.

###### Question
Describe your question here as clear as possible.
