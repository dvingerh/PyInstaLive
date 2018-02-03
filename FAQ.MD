## Frequently asked questions


### I'm unable to log in, what do I do?
Login errors such as `Challenge required` are usually caused by one of the following:

- You have entered invalid account credentials.
- You are using PyInstaLive from a different location/IP address compared to where you are usually logged in. (This includes things like your phone's 4G network vs your home's internet connection)
- Your IP address or account has been flagged as spam or suspicious.

The reasons above are things I have no control over, so there's no direct way for me to solve your problem. You can try checking out the URL which you can find in the response text you'll be able to see when such errors occur:
```
(Code: 400, Response: {"message": "challenge_required", "challenge": {"url": "https://i.instagram.com/challenge/XXXXX/XXXX/", "api_path": "/challenge/XXXXX/XXXXXX/", "lock": true, "logout": false, "native_flow": true}, "status": "fail", "error_type": "checkpoint_challenge_required"})
```

If that doesn't help you out either I recommend creating a new temporary Instagram account (on the device and internet connection you will be using PyInstaLive with) and use that instead.


### How do I record multiple users at the same time?

#### Windows


```batch
cd C:\PyInstaLive
:loop
pyinstalive -u "username" -p "password" -r "live-username"
timeout 10 > nul
goto loop
```
Make a new text file and copy the above contents. Edit the PyInstaLive command to your liking. Make sure to save the text as a .bat file. Do this for each user you want to record and run the scripts concurrently.

Increase the timeout by at least 5 seconds or more for each user you want to record to lessen the chances of getting blocked by Instagram.

Make sure there is a configuration file called pyinstalive.ini in the directory you want to run PyInstaLive from. (Use `cd` to navigate to that directory if you put this script in a different location.)

#### Linux / MacOS (not tested)

```shell
while true
do
    cd /home/default/PyInstaLive/
    pyinstalive -u "username" -p "password" -r "live-username"
    sleep 10
done
```
Make a new text file and copy the above contents. Edit the PyInstaLive command to your liking. Make sure to save the text as a .sh file.
You must make the script executable with `chmod +x <filename>`. Use Google.
Do this for each user you want to record and run the scripts concurrently.

Increase the timeout by at least 5 seconds or more for each user you want to record to lessen the chances of getting blocked by Instagram.

Make sure there is a configuration file called pyinstalive.ini in the directory you want to run PyInstaLive from. (Use `cd` to navigate to that directory if you put this script in a different location.)

### How can I run PyInstaLive 24/7 so I won't miss a livestream?

Use the scripts provided in the previous question, they'll infinitely run the PyInstaLive command you entered there. You'll need to have a computer or other device running this script 24/7 for this to work, obviously.
