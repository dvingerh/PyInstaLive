import argparse
import configparser
import logging
import os.path
import sys
import subprocess
import time

from .auth import login
from .logger import log, seperator, supports_color
from .downloader import main
from .settings import settings

try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen

script_version = "2.2.9_testing"
python_version = sys.version.split(' ')[0]
bool_values = {'True', 'False'}

def check_ffmpeg():
	try:
		FNULL = open(os.devnull, 'w')
		subprocess.call(["ffmpeg"], stdout=FNULL, stderr=subprocess.STDOUT)
		return True
	except OSError as e:
		return False


def check_config_validity(config):
	try:
		settings.username = config.get('pyinstalive', 'username')
		settings.password = config.get('pyinstalive', 'password')



		try:
			settings.show_cookie_expiry = config.get('pyinstalive', 'show_cookie_expiry').title()
			if not settings.show_cookie_expiry in bool_values:
				log("[W] Invalid or missing setting detected for 'show_cookie_expiry', using default value (True)", "YELLOW")
				settings.show_cookie_expiry = 'true'
		except:
			log("[W] Invalid or missing setting detected for 'show_cookie_expiry', using default value (True)", "YELLOW")
			settings.show_cookie_expiry = 'true'



		try:
			settings.clear_temp_files = config.get('pyinstalive', 'clear_temp_files').title()
			if not settings.clear_temp_files in bool_values:
				log("[W] Invalid or missing setting detected for 'clear_temp_files', using default value (True)", "YELLOW")
				settings.clear_temp_files = 'true'
		except:
			log("[W] Invalid or missing setting detected for 'clear_temp_files', using default value (True)", "YELLOW")
			settings.clear_temp_files = 'true'


		try:
			settings.save_replays = config.get('pyinstalive', 'save_replays').title()
			if not settings.save_replays in bool_values:
				log("[W] Invalid or missing setting detected for 'save_replays', using default value (True)", "YELLOW")
				settings.save_replays = 'true'
		except:
			log("[W] Invalid or missing setting detected for 'save_replays', using default value (True)", "YELLOW")
			settings.save_replays = 'true'



		try:
			settings.save_path = config.get('pyinstalive', 'save_path')

			if (os.path.exists(settings.save_path)):
				pass
			else:
				log("[W] Invalid or missing setting detected for 'save_path', falling back to path: " + os.getcwd(), "YELLOW")
				settings.save_path = os.getcwd()

			if not settings.save_path.endswith('/'):
				settings.save_path = settings.save_path + '/'
		except:
			log("[W] Invalid or missing setting detected for 'save_path', falling back to path: " + os.getcwd(), "YELLOW")
			settings.save_path = os.getcwd()

		if not (len(settings.username) > 0):
			log("[E] Invalid or missing setting detected for 'username'.", "RED")
			return False

		if not (len(settings.password) > 0):
			log("[E] Invalid or missing setting detected for 'password'.", "RED")
			return False

		return True
	except Exception as e:
		return False

def show_info():
	log("[I] To see all the available flags, use the -h flag.", "BLUE")
	log("", "GREEN")
	log("[I] PyInstaLive version:    	" + script_version, "GREEN")
	log("[I] Python version:         	" + python_version, "GREEN")
	if check_ffmpeg() == False:
		log("[E] FFmpeg framework:       	Not found", "RED")
	else:
		log("[I] FFmpeg framework:       	Available", "GREEN")
	if not os.path.isfile('credentials.json'):
		log("[W] Cookie file:            	Not found", "YELLOW")
	else:
		log("[I] Cookie file:            	Available", "GREEN")
	log("[I] CLI supports color:     	" + str(supports_color()), "GREEN")

	if os.path.exists('pyinstalive.ini'):
		log("[I] Config file:", "GREEN")
		log("", "GREEN")
		with open('pyinstalive.ini') as f:
			for line in f:
				log("    " + line.rstrip(), "YELLOW")
	else:
		log("[E] Config file:	    	Not found", "RED")
	log("", "GREEN")
	log("[I] End of PyInstaLive information screen.", "GREEN")
	seperator("GREEN")

def new_config():
	try:
		if os.path.exists('pyinstalive.ini'):
			log("[I] A configuration file is already present:", "GREEN")
			log("", "GREEN")
			with open('pyinstalive.ini') as f:
				for line in f:
					log("    " + line.rstrip(), "YELLOW")
			log("", "GREEN")
			log("[W] To create a default config file, delete 'pyinstalive.ini' and ", "YELLOW")
			log("    run this script again.", "YELLOW")
			seperator("GREEN")
		else:
			try:
				log("[W] Could not find configuration file, creating a default one ...", "YELLOW")
				config_template = "[pyinstalive]\nusername = johndoe\npassword = grapefruits\nsave_path = /\nshow_cookie_expiry = true\nclear_temp_files = false\nsave_replays = true"
				config_file = open("pyinstalive.ini", "w")
				config_file.write(config_template)
				config_file.close()
				log("[W] Edit the created 'pyinstalive.ini' file and run this script again.", "YELLOW")
				seperator("GREEN")
				sys.exit(0)
			except Exception as e:
				log("[E] Could not create default config file: " + str(e), "RED")
				log("[W] You must manually create and edit it with the following template: ", "YELLOW")
				log("", "GREEN")
				log(config_template, "YELLOW")
				log("", "GREEN")
				log("[W] Save it as 'pyinstalive.ini' and run this script again.", "YELLOW")
				log("", "GREEN")
	except Exception as e:
		log("[E] An error occurred: " + str(e), "RED")
		log("[W] If you don't have a configuration file, you must", "YELLOW")
		log("    manually create and edit it with the following template: ", "YELLOW")
		log("", "GREEN")
		log(config_template, "YELLOW")
		log("", "GREEN")
		log("[W] Save it as 'pyinstalive.ini' and run this script again.", "YELLOW")
		log("", "GREEN")

def update():
	log("[I] Checking for updates ...", "GREEN")
	latest_version = urlopen("https://raw.githubusercontent.com/notcammy/PyInstaLive/master/VERSION").read().decode('utf-8').rstrip()
	if (str(script_version) != str(latest_version)):
		try:
			sys.stdout.write("\033[92m[I] Current version: {}\n[I] Latest version: {}\n[I] Do you want to update? [y/n]: ".format(script_version, latest_version))
			if python_version[0] == "2":
				answer = raw_input()
			else:
				answer = input()
			if not answer or answer[0].lower() not in {'y', 'n'}:
			   log("[E] Invalid answer provided, aborting ...", "RED")
			   seperator("GREEN")
			   exit(1)
			elif answer[0].lower() == 'y':
			   log("", "ENDC")
			   log("[I] In case update fails, manually run the following command (optionally with sudo):\n", "BLUE")
			   log("    pip install git+https://github.com/notcammy/PyInstaLive.git@{} --process-dependency-links --upgrade\n".format(latest_version), "BLUE")
			   log("[I] Starting update command in 3 seconds ...", "BLUE")
			   time.sleep(3)
			   subprocess.call(["pip", "install", "git+https://github.com/notcammy/PyInstaLive.git@" + latest_version, "--process-dependency-links", "--upgrade"])
			elif answer[0].lower() == 'n':
				log('[I] Aborting ...', "GREEN")
				seperator("GREEN")
				exit(0)
		except Exception as e:
			print(str(e))
			sys.exit(0)	
		except KeyboardInterrupt:
			log('\n[I] Aborting ...', "GREEN")
			seperator("GREEN")
			exit(0)
	else:
		log("[I] You are already using the latest version.", "GREEN")
		sys.exit(0)


def run():
	seperator("GREEN")
	log('PYINSTALIVE (SCRIPT V{} - PYTHON V{}) - {}'.format(script_version, python_version, time.strftime('%H:%M:%S %p')), "GREEN")
	seperator("GREEN")

	logging.disable(logging.CRITICAL)

	config = configparser.ConfigParser()
	parser = argparse.ArgumentParser(description='You are running PyInstaLive ' + script_version + " with Python " + python_version)
	parser.add_argument('-u', '--username', dest='username', type=str, required=False, help="Instagram username to login with.")
	parser.add_argument('-p', '--password', dest='password', type=str, required=False, help="Instagram password to login with.")
	parser.add_argument('-r', '--record', dest='record', type=str, required=False, help="The username of the Instagram whose livestream or replay you want to save.")
	parser.add_argument('-i', '--info', dest='info', action='store_true', help="View information about PyInstaLive.")
	parser.add_argument('-c', '--config', dest='config', action='store_true', help="Create a default configuration file if it doesn't exist.")
	parser.add_argument('--update', dest="update", action='store_true', help="Check for updates and prompt to install them if available.")
	args = parser.parse_args()

	if (args.update == True):
		update()
		sys.exit(0)

	if (args.config == True):
		new_config()
		sys.exit(0)

	if (args.username == None and args.password == None and args.record == None and args.info == False and args.config == False and args.upgrade == False) or (args.info != False):
		show_info()
		sys.exit(0)

	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception:
			log("[E] Could not read configuration file. Try passing the required arguments manually.", "RED")
			seperator("GREEN")
	else:
		new_config()
		sys.exit(1)


	if check_config_validity(config):
		if check_ffmpeg() == False:
			log("[E] Could not find ffmpeg, the script will now exit. ", "RED")
			seperator("GREEN")
			sys.exit(1)

		if (args.username is not None) and (args.password is not None):
			api = login(args.username, args.password, settings.show_cookie_expiry)
		else:
			api = login(settings.username, settings.password, settings.show_cookie_expiry)

		main(api, args.record, settings)
	else:
		log("[E] The configuration file is not valid. Please check your configuration settings and try again.", "RED")
		seperator("GREEN")
		sys.exit(0)
