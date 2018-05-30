import argparse
import configparser
import logging
import os.path
import subprocess
import sys
import time
import shutil
import json

from .auth import login
from .downloader import main
from .logger import log
from .logger import seperator
from .logger import supports_color
from .settings import settings

script_version = "2.5.5"
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
			settings.log_to_file = config.get('pyinstalive', 'log_to_file').title()
			if not settings.log_to_file in bool_values:
				log("[W] Invalid or missing setting detected for 'log_to_file', using default value (False)", "YELLOW")
				settings.log_to_file = 'False'
				has_thrown_errors = True
		except:
			log("[W] Invalid or missing setting detected for 'log_to_file', using default value (False)", "YELLOW")
			settings.log_to_file = 'False'
			has_thrown_errors = True



		try:
			settings.run_at_start = config.get('pyinstalive', 'run_at_start').replace("\\", "\\\\")
			if not settings.run_at_start:
				settings.run_at_start = "None"
		except:
			log("[W] Invalid or missing settings detected for 'run_at_start', using default value (None)", "YELLOW")
			settings.run_at_start = "None"
			has_thrown_errors = True



		try:
			settings.run_at_finish = config.get('pyinstalive', 'run_at_finish').replace("\\", "\\\\")
			if not settings.run_at_finish:
				settings.run_at_finish = "None"
		except:
			log("[W] Invalid or missing settings detected for 'run_at_finish', using default value (None)", "YELLOW")
			settings.run_at_finish = "None"
			has_thrown_errors = True


		try:
			settings.save_comments = config.get('pyinstalive', 'save_comments').title()
			wide_build = sys.maxunicode > 65536
			if sys.version.split(' ')[0].startswith('2') and settings.save_comments == "True" and not wide_build:
				log("[W] Your Python 2 build does not support wide unicode characters.\n[W] This means characters such as emojis will not be saved.", "YELLOW")
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
				log("[W] Invalid or missing setting detected for 'save_path', falling back to path: {:s}".format(os.getcwd()), "YELLOW")
				settings.save_path = os.getcwd()
				has_thrown_errors = True

			if not settings.save_path.endswith('/'):
				settings.save_path = settings.save_path + '/'
		except:
			log("[W] Invalid or missing setting detected for 'save_path', falling back to path: {:s}".format(os.getcwd()), "YELLOW")
			settings.save_path = os.getcwd()
			has_thrown_errors = True


		if has_thrown_errors:
			seperator("GREEN")

		return True
	except Exception as e:
		print(str(e))
		return False



def show_info(config):
	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception as e:
			log("[E] Could not read configuration file: {:s}".format(str(e)), "RED")
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
				with open(file) as data_file:    
					try:
						json_data = json.load(data_file)
						if (json_data.get('created_ts')):
							cookie_files.append(file)
					except Exception as e:
						pass
			if settings.username == file.replace(".json", ''):
				cookie_from_config = file
	except Exception as e:
		log("[W] Could not check for cookie files: {:s}".format(str(e)), "YELLOW")
		log("", "ENDC")
	log("[I] To see all the available flags, use the -h flag.", "BLUE")
	log("", "GREEN")
	log("[I] PyInstaLive version:    	{:s}".format(script_version), "GREEN")
	log("[I] Python version:         	{:s}".format(python_version), "GREEN")
	if not check_ffmpeg():
		log("[E] FFmpeg framework:       	Not found", "RED")
	else:
		log("[I] FFmpeg framework:       	Available", "GREEN")

	if (len(cookie_from_config) > 0):
		log("[I] Cookie files:            	{:s} ({:s} matches config user)".format(str(len(cookie_files)), cookie_from_config), "GREEN")
	elif len(cookie_files) > 0:
		log("[I] Cookie files:            	{:s}".format(str(len(cookie_files))), "GREEN")
	else:
		log("[W] Cookie files:            	None found", "YELLOW")

	log("[I] CLI supports color:     	{:s}".format(str(supports_color()[0])), "GREEN")
	log("[I] File to run at start:       {:s}".format(settings.run_at_start), "GREEN")
	log("[I] File to run at finish:      {:s}".format(settings.run_at_finish), "GREEN")
	log("", "GREEN")


	if os.path.exists('pyinstalive.ini'):
		log("[I] Config file:", "GREEN")
		log("", "GREEN")
		with open('pyinstalive.ini') as f:
			for line in f:
				log("    {:s}".format(line.rstrip()), "YELLOW")
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
					log("    {:s}".format(line.rstrip()), "YELLOW")
			log("", "GREEN")
			log("[I] To create a default config file, delete 'pyinstalive.ini' and ", "GREEN")
			log("    run this script again.", "GREEN")
			seperator("GREEN")
		else:
			try:
				log("[W] Could not find configuration file, creating a default one...", "YELLOW")
				config_template = "[pyinstalive]\nusername = johndoe\npassword = grapefruits\nsave_path = {:s}\nshow_cookie_expiry = true\nclear_temp_files = false\nsave_replays = true\nrun_at_start = \nrun_at_finish = \nsave_comments = false\nlog_to_file = false\n".format(os.getcwd())
				config_file = open("pyinstalive.ini", "w")
				config_file.write(config_template)
				config_file.close()
				log("[W] Edit the created 'pyinstalive.ini' file and run this script again.", "YELLOW")
				seperator("GREEN")
				sys.exit(0)
			except Exception as e:
				log("[E] Could not create default config file: {:s}".format(str(e)), "RED")
				log("[W] You must manually create and edit it with the following template: ", "YELLOW")
				log("", "GREEN")
				log(config_template, "YELLOW")
				log("", "GREEN")
				log("[W] Save it as 'pyinstalive.ini' and run this script again.", "YELLOW")
				seperator("GREEN")
	except Exception as e:
		log("[E] An error occurred: {:s}".format(str(e)), "RED")
		log("[W] If you don't have a configuration file, you must", "YELLOW")
		log("    manually create and edit it with the following template: ", "YELLOW")
		log("", "GREEN")
		log(config_template, "YELLOW")
		log("", "GREEN")
		log("[W] Save it as 'pyinstalive.ini' and run this script again.", "YELLOW")
		seperator("GREEN")



def clean_download_dir():
	dir_delcount = 0
	error_count = 0
	lock_count = 0

	log('[I] Cleaning up temporary files and folders...', "GREEN")
	try:
		if sys.version.split(' ')[0].startswith('2'):
			directories = (os.walk(settings.save_path).next()[1])
			files = (os.walk(settings.save_path).next()[2])
		else:
			directories = (os.walk(settings.save_path).__next__()[1])
			files = (os.walk(settings.save_path).__next__()[2])

		for directory in directories:
			if directory.endswith('_downloads'):
				if not any(filename.endswith('.lock') for filename in os.listdir(settings.save_path + directory)):
					try:
						shutil.rmtree(settings.save_path + directory)
						dir_delcount += 1
					except Exception as e:
						log("[E] Could not remove temp folder: {:s}".format(str(e)), "RED")
						error_count += 1
				else:
					lock_count += 1
		seperator("GREEN")
		log('[I] The cleanup has finished.', "YELLOW")
		if dir_delcount == 0 and error_count == 0 and lock_count == 0:
			log('[I] No folders were removed.', "YELLOW")
			seperator("GREEN")
			return
		log('[I] Folders removed:     {:d}'.format(dir_delcount), "YELLOW")
		log('[I] Locked folders:      {:d}'.format(lock_count), "YELLOW")
		log('[I] Errors:              {:d}'.format(error_count), "YELLOW")
		seperator("GREEN")
	except KeyboardInterrupt as e:
		seperator("GREEN")
		log("[W] The cleanup has been aborted.", "YELLOW")
		if dir_delcount == 0 and error_count == 0 and lock_count == 0:
			log('[I] No folders were removed.', "YELLOW")
			seperator("GREEN")
			return
		log('[I] Folders removed:     {:d}'.format(dir_delcount), "YELLOW")
		log('[I] Locked folders:      {:d}'.format(lock_count), "YELLOW")
		log('[I] Errors:              {:d}'.format(error_count), "YELLOW")
		seperator("GREEN")

def run():
	logging.disable(logging.CRITICAL)
	config = configparser.ConfigParser()
	parser = argparse.ArgumentParser(description="You are running PyInstaLive {:s} using Python {:s}".format(script_version, python_version))
	parser.add_argument('-u', '--username', dest='username', type=str, required=False, help="Instagram username to login with.")
	parser.add_argument('-p', '--password', dest='password', type=str, required=False, help="Instagram password to login with.")
	parser.add_argument('-r', '--record', dest='download', type=str, required=False, help="The username of the user whose livestream or replay you want to save.")
	parser.add_argument('-d', '--download', dest='download', type=str, required=False, help="The username of the user whose livestream or replay you want to save.")
	parser.add_argument('-i', '--info', dest='info', action='store_true', help="View information about PyInstaLive.")
	parser.add_argument('-c', '--config', dest='config', action='store_true', help="Create a default configuration file if it doesn't exist.")
	parser.add_argument('-nr', '--noreplays', dest='noreplays', action='store_true', help="When used, do not check for any available replays.")
	parser.add_argument('-cl', '--clean', dest='clean', action='store_true', help="PyInstaLive will clean the current download folder of all leftover files.")

	# Workaround to 'disable' argument abbreviations
	parser.add_argument('--usernamx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--passworx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--recorx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--infx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--confix', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--noreplayx', help=argparse.SUPPRESS, metavar='IGNORE') 
	parser.add_argument('--cleax', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('-cx', help=argparse.SUPPRESS, metavar='IGNORE')


	args, unknown = parser.parse_known_args()


	try:
		config.read('pyinstalive.ini')
		settings.log_to_file = config.get('pyinstalive', 'log_to_file').title()
		if not settings.log_to_file in bool_values:
			settings.log_to_file = 'False'
		elif settings.log_to_file == "True":
			if args.download:
				settings.user_to_download = args.download
			else:
				settings.user_to_download = "log"
			try:
				with open("pyinstalive_{:s}.log".format(settings.user_to_download),"a+") as f:
					f.write("\n")
					f.close()
			except:
				pass
	except Exception as e:
		settings.log_to_file = 'False'
		pass # Pretend nothing happened

	seperator("GREEN")
	log('PYINSTALIVE (SCRIPT V{:s} - PYTHON V{:s}) - {:s}'.format(script_version, python_version, time.strftime('%I:%M:%S %p')), "GREEN")
	seperator("GREEN")

	if unknown:
		log("[E] The following invalid argument(s) were provided: ", "RED") 
		log('', "GREEN") 
		log('    ' + ' '.join(unknown), "YELLOW") 
		log('', "GREEN")
		if (supports_color()[1] == True):
			log("[I] \033[94mpyinstalive -h\033[92m can be used to display command help.", "GREEN")
		else:
			log("[I] pyinstalive -h can be used to display command help.", "GREEN")
		seperator("GREEN")
		exit(1)

	if (args.info) or (not
	args.username and not
	args.password and not
	args.download and not
	args.info and not
	args.config and not
	args.noreplays and not
	args.clean):
		show_info(config)
		sys.exit(0)
	
	if (args.config):
		new_config()
		sys.exit(0)


	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception:
			log("[E] Could not read configuration file.", "RED")
			seperator("GREEN")
	else:
		new_config()
		sys.exit(1)


	if check_config_validity(config):
		if (args.clean):
			clean_download_dir()
			sys.exit(0)

		if not check_ffmpeg():
			log("[E] Could not find ffmpeg, the script will now exit. ", "RED")
			seperator("GREEN")
			sys.exit(1)

		if (args.download == None):
			log("[E] Missing --download argument. Please specify an Instagram username.", "RED")
			seperator("GREEN")
			sys.exit(1)

		if (args.noreplays):
			settings.save_replays = "false"

		if (args.username is not None) and (args.password is not None):
			api = login(args.username, args.password, settings.show_cookie_expiry, True)
		elif (args.username is not None) or (args.password is not None):
			log("[W] Missing -u or -p arguments, falling back to config file...", "YELLOW")
			if (not len(settings.username) > 0) or (not len(settings.password) > 0):
				log("[E] Username or password are missing. Please check your configuration settings and try again.", "RED")
				seperator("GREEN")
				sys.exit(1)
			else:
				api = login(settings.username, settings.password, settings.show_cookie_expiry, False)
		else:
			if (not len(settings.username) > 0) or (not len(settings.password) > 0):
				log("[E] Username or password are missing. Please check your configuration settings and try again.", "RED")
				seperator("GREEN")
				sys.exit(1)
			else:
				api = login(settings.username, settings.password, settings.show_cookie_expiry, False)

		main(api, args.download, settings)

	else:
		log("[E] The configuration file is not valid. Please check your configuration settings and try again.", "RED")
		seperator("GREEN")
		sys.exit(1)