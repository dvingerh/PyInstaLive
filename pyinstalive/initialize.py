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

script_version = "2.4.3"
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
		has_thrown_errors = False
		settings.username = config.get('pyinstalive', 'username')
		settings.password = config.get('pyinstalive', 'password')

		try:
			settings.show_cookie_expiry = config.get('pyinstalive', 'show_cookie_expiry').title()
			if not settings.show_cookie_expiry in bool_values:
				log("[W] Invalid or missing setting detected for 'show_cookie_expiry', using default value (True)", "YELLOW")
				settings.show_cookie_expiry = 'true'
				has_thrown_errors = True
		except:
			log("[W] Invalid or missing setting detected for 'show_cookie_expiry', using default value (True)", "YELLOW")
			settings.show_cookie_expiry = 'true'
			has_thrown_errors = True



		try:
			settings.clear_temp_files = config.get('pyinstalive', 'clear_temp_files').title()
			if not settings.clear_temp_files in bool_values:
				log("[W] Invalid or missing setting detected for 'clear_temp_files', using default value (True)", "YELLOW")
				settings.clear_temp_files = 'true'
				has_thrown_errors = True
		except:
			log("[W] Invalid or missing setting detected for 'clear_temp_files', using default value (True)", "YELLOW")
			settings.clear_temp_files = 'true'
			has_thrown_errors = True



		try:
			settings.save_replays = config.get('pyinstalive', 'save_replays').title()
			if not settings.save_replays in bool_values:
				log("[W] Invalid or missing setting detected for 'save_replays', using default value (True)", "YELLOW")
				settings.save_replays = 'true'
				has_thrown_errors = True
		except:
			log("[W] Invalid or missing setting detected for 'save_replays', using default value (True)", "YELLOW")
			settings.save_replays = 'true'
			has_thrown_errors = True



		try:
			settings.run_at_start = config.get('pyinstalive', 'run_at_start')
			if (settings.run_at_start):
				if not os.path.isfile(settings.run_at_start):
					log("[W] Path to file given for 'run_at_start' does not exist, using default value (None)", "YELLOW")
					settings.run_at_start = "None"
					has_thrown_errors = True
				else:
					if not settings.run_at_start.split('.')[-1] == 'py':
						log("[W] File given for 'run_at_start' is not a Python script, using default value (None)", "YELLOW")
						settings.run_at_start = "None"
						has_thrown_errors = True
			else:
				settings.run_at_start = "None"
		except:
			log("[W] Invalid or missing settings detected for 'run_at_start', using default value (None)", "YELLOW")
			settings.run_at_start = "None"
			has_thrown_errors = True



		try:
			settings.run_at_finish = config.get('pyinstalive', 'run_at_finish')
			if (settings.run_at_finish):
				if not os.path.isfile(settings.run_at_finish):
					log("[W] Path to file given for 'run_at_finish' does not exist, using default value (None)", "YELLOW")
					settings.run_at_finish = "None"
					has_thrown_errors = True
				else:
					if not settings.run_at_finish.split('.')[-1] == 'py':
						log("[W] File given for 'run_at_finish' is not a Python script, using default value (None)", "YELLOW")
						settings.run_at_finish = "None"
						has_thrown_errors = True
			else:
				settings.run_at_finish = "None"

		except:
			log("[W] Invalid or missing settings detected for 'run_at_finish', using default value (None)", "YELLOW")
			settings.run_at_finish = "None"
			has_thrown_errors = True


		try:
			settings.save_comments = config.get('pyinstalive', 'save_comments').title()
			if sys.version.split(' ')[0].startswith('2') and settings.save_comments == "True":
				log("[W] Comment saving is not supported in Python 2 and will be ignored.", "YELLOW")
				settings.save_comments = 'false'
				has_thrown_errors = True
			else:
				if not settings.show_cookie_expiry in bool_values:
					log("[W] Invalid or missing setting detected for 'save_comments', using default value (False)", "YELLOW")
					settings.save_comments = 'false'
					has_thrown_errors = True
		except:
			log("[W] Invalid or missing setting detected for 'save_comments', using default value (False)", "YELLOW")
			settings.save_comments = 'false'
			has_thrown_errors = True

		try:
			settings.save_path = config.get('pyinstalive', 'save_path')

			if (os.path.exists(settings.save_path)):
				pass
			else:
				log("[W] Invalid or missing setting detected for 'save_path', falling back to path: " + os.getcwd(), "YELLOW")
				settings.save_path = os.getcwd()
				has_thrown_errors = True

			if not settings.save_path.endswith('/'):
				settings.save_path = settings.save_path + '/'
		except:
			log("[W] Invalid or missing setting detected for 'save_path', falling back to path: " + os.getcwd(), "YELLOW")
			settings.save_path = os.getcwd()
			has_thrown_errors = True

		if has_thrown_errors:
			seperator("GREEN")

		if not (len(settings.username) > 0):
			log("[E] Invalid or missing setting detected for 'username'.", "RED")
			return False

		if not (len(settings.password) > 0):
			log("[E] Invalid or missing setting detected for 'password'.", "RED")
			return False

		return True
	except Exception as e:
		return False

def show_info(config):
	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception:
			log("[E] Could not read configuration file.", "RED")
			seperator("GREEN")
	else:
		new_config()
		sys.exit(1)

	if not check_config_validity(config):
		log("[W] Config file is not valid, some information may be inaccurate.", "YELLOW")
		log("", "GREEN")

	cookie_files = []
	cookie_from_config = ''
	try:
		for file in os.listdir(os.getcwd()):
			if file.endswith(".json"):
				cookie_files.append(file)
			if settings.username == file.replace(".json", ''):
				cookie_from_config = file
	except Exception as e:
		log("[W] Could not check for cookie files: " + str(e), "YELLOW")
		log("", "ENDC")
	log("[I] To see all the available flags, use the -h flag.", "BLUE")
	log("", "GREEN")
	log("[I] PyInstaLive version:    	" + script_version, "GREEN")
	log("[I] Python version:         	" + python_version, "GREEN")
	if check_ffmpeg() == False:
		log("[E] FFmpeg framework:       	Not found", "RED")
	else:
		log("[I] FFmpeg framework:       	Available", "GREEN")

	if (len(cookie_from_config) > 0):
		log("[I] Cookie files:            	{} ({} matches config user)".format(str(len(cookie_files)), cookie_from_config), "GREEN")
	elif len(cookie_files) > 0:
		log("[I] Cookie files:            	{}".format(str(len(cookie_files))), "GREEN")
	else:
		log("[W] Cookie files:            	None found", "YELLOW")

	log("[I] CLI supports color:     	" + str(supports_color()), "GREEN")
	log("[I] File to run at start:       " + settings.run_at_start, "GREEN")
	log("[I] File to run at finish:      " + settings.run_at_finish, "GREEN")
	log("", "GREEN")


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
				log("[W] Could not find configuration file, creating a default one...", "YELLOW")
				config_template = "[pyinstalive]\nusername = johndoe\npassword = grapefruits\nsave_path = " + os.getcwd() + "\nshow_cookie_expiry = true\nclear_temp_files = false\nsave_replays = true\nrun_at_start = \nrun_at_finish = \nsave_comments = false\n"
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
				seperator("GREEN")
	except Exception as e:
		log("[E] An error occurred: " + str(e), "RED")
		log("[W] If you don't have a configuration file, you must", "YELLOW")
		log("    manually create and edit it with the following template: ", "YELLOW")
		log("", "GREEN")
		log(config_template, "YELLOW")
		log("", "GREEN")
		log("[W] Save it as 'pyinstalive.ini' and run this script again.", "YELLOW")
		seperator("GREEN")



def run():
	seperator("GREEN")
	log('PYINSTALIVE (SCRIPT V{} - PYTHON V{}) - {}'.format(script_version, python_version, time.strftime('%I:%M:%S %p')), "GREEN")
	seperator("GREEN")

	logging.disable(logging.CRITICAL)

	config = configparser.ConfigParser()
	parser = argparse.ArgumentParser(description='You are running PyInstaLive ' + script_version + " using Python " + python_version)
	parser.add_argument('-u', '--username', dest='username', type=str, required=False, help="Instagram username to login with.")
	parser.add_argument('-p', '--password', dest='password', type=str, required=False, help="Instagram password to login with.")
	parser.add_argument('-r', '--record', dest='record', type=str, required=False, help="The username of the user whose livestream or replay you want to save.")
	parser.add_argument('-i', '--info', dest='info', action='store_true', help="View information about PyInstaLive.")
	parser.add_argument('-c', '--config', dest='config', action='store_true', help="Create a default configuration file if it doesn't exist.")
	parser.add_argument('-nr', '--noreplays', dest='noreplays', action='store_true', help="When used, do not check for any available replays.")


	# Workaround to 'disable' argument abbreviations
	parser.add_argument('--usernamx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--passworx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--recorx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--infx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--confix', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--noreplayx', help=argparse.SUPPRESS, metavar='IGNORE')

	# Erase line that tells the user the error has to do with ambiguous arguments
	try:
		args = parser.parse_args()
	except SystemExit as e:
		args_raw = sys.argv[1:]
		if "-h" not in args_raw and "--help" not in args_raw:
			CURSOR_UP_ONE = '\x1b[1A'
			ERASE_LINE = '\x1b[2K'
			log(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE + "[E] Invalid argument(s) were provided in command: " + ' ' * 50, "RED")
			log("   pyinstalive " + ' '.join(args_raw), "YELLOW")
			log("\n[I] Usage for PyInstaLive is printed below.\n", "GREEN")
			parser.print_help()
			sys.exit(1)
		else:
			sys.exit(0)

	if (args.username == None 
		and args.password == None 
		and args.record == None 
		and args.info == False 
		and args.config == False) or (args.info != False):
		show_info(config)
		sys.exit(0)
	
	if (args.config == True):
		new_config()
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

		if (args.record == None):
			log("[E] Missing --record argument. Please specify an Instagram username.", "RED")
			seperator("GREEN")
			sys.exit(1)

		if (args.noreplays == True):
			settings.save_replays = "false"

		if (args.username is not None) and (args.password is not None):
			api = login(args.username, args.password, settings.show_cookie_expiry, True)
		else:
			if (args.username is not None) or (args.password is not None):
				log("[W] Missing -u or -p arguments, falling back to config login...", "YELLOW")
			api = login(settings.username, settings.password, settings.show_cookie_expiry, False)

		main(api, args.record, settings)

	else:
		log("[E] The configuration file is not valid. Please check your configuration settings and try again.", "RED")
		seperator("GREEN")
		sys.exit(0)
