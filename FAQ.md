## Frequently asked questions


### I'm unable to log in, what do I do?
Login errors such as `Challenge required` are usually caused by one of the following:

- You are using PyInstaLive from a different location, device or IP address compared to where you are usually logged in.
- Your IP address or account has been flagged as spam or suspicious.

Try to create a new temporary Instagram account (preferably on the device most importantly using the internet connection you will be using PyInstaLive with) and use that instead. Also make sure to check out [this issue](https://github.com/notcammy/PyInstaLive/issues/57) for more relevant information.

### I get a Rate Limit related error, how do I solve this?
This means you are making too many requests to Instagram and is usually the case when you try to check and download livestreams of multiple users at the same time by using a script (as seen below). Increase the timeout for the scripts or decrease the amount of users you are checking.

### How do I download livestreams of multiple users at the same time?

#### Option 1 - Checking your following users

You can use the `--download-following` function to check for available livestreams from your following user list. Read the [Help Documents](https://github.com/notcammy/PyInstaLive/blob/master/MOREHELP.md) for more information.

#### Option 2 - Using external scripts
##### Note: Continuously checking for livestreams with an external script is considered suspicious behaviour by Instagram. Use a timeout as large as possible to decrease the chances of your account, device or IP from getting flagged as suspicious and getting blocked as a result of that. Use the scripts below at your own risk.

###### Windows


```batch
:loop
pyinstalive -u "username" -p "password" -d "live-username"
timeout 60 > nul
goto loop
```
Make a new text file and copy the above contents. Edit the PyInstaLive command to your liking. Make sure to save the text as a .bat file. Do this for each user you want to download a livestream of and run the scripts concurrently.

Make sure there is a configuration file called pyinstalive.ini in the directory you want to run PyInstaLive from. (Use `cd` to navigate to that directory if you put this script in a different location.)

###### Linux / MacOS

```shell
while true
do
    pyinstalive -u "username" -p "password" -d "live-username"
    sleep 60
done
```
Make a new text file and copy the above contents. Edit the PyInstaLive command to your liking. Make sure to save the text as a .sh file.
You must make the script executable with `chmod +x <filename>`. Use Google.
Do this for each user you want to download a livestream of and run the scripts concurrently.

Make sure there is a configuration file called pyinstalive.ini in the directory you want to run PyInstaLive from. (Use `cd` to navigate to that directory if you put this script in a different location.)

### How can I run PyInstaLive 24/7 so I won't miss a livestream?

Use the scripts provided in the previous question, they'll infinitely run the PyInstaLive command you entered there. You'll need to have a computer or other device running this script 24/7 for this to work, obviously.

### Can I use PyInstaLive and [livestream_dl](https://github.com/taengstagram/instagram-livestream-downloader) concurrently?

No. This is because livestream_dl is no longer being maintained and as such uses an older version of libraries required by PyInstaLive. Installing PyInstaLive and livestream_dl on different Python versions (2/3) will probably work though.

### PyInstaLive failed to assemble a video file after the download has ended. What do I do?

If it failed to assemble a video there are two options:
* Use the `--assemble` command as described in the [FAQ](https://github.com/notcammy/PyInstaLive/blob/master/MOREHELP.md#commands).

If that didn't work, you can still attempt to concatenate the segment files yourself:

* Open the segment video directory in your command line.
  * Windows: `copy /b *.m4v video.mp4 && copy /b *.m4a audio.mp4 && ffmpeg -i video.mp4 -i audio.mp4 -c copy output.mp4`
  * Linux: `cat  *.m4v > video.mp4 && cat  *.m4a > audio.mp4 && ffmpeg -i video.mp4 -i audio.mp4 -c copy output.mp4`