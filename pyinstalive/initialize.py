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
from .downloader import start_single, start_multiple
from .logger import log_seperator, supports_color, log_info_blue, log_info_green, log_warn, log_error, log_whiteline, log_plain
from .settings import settings

script_version = "2.5.6@master"
python_version = sys.version.split(' ')[0]
bool_values = {'True', 'False'}

def check_ffmpeg():
	try:
		FNULL = open(os.devnull, 'w')
		subprocess.call(["ffmpeg"], stdout=FNULL, stderr=subprocess.STDOUT)
		return True
	except OSError as e:
		return False

def check_pyinstalive():
	try:
		FNULL = open(os.devnull, 'w')
		subprocess.call(["pyinstalive"], stdout=FNULL, stderr=subprocess.STDOUT)
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
				log_warn("Invalid or missing setting detected for 'show_cookie_expiry', using default value (True)")
				settings.show_cookie_expiry = 'true'
				has_thrown_errors = True
		except:
			log_warn("Invalid or missing setting detected for 'show_cookie_expiry', using default value (True)")
			settings.show_cookie_expiry = 'true'
			has_thrown_errors = True



		try:
			settings.clear_temp_files = config.get('pyinstalive', 'clear_temp_files').title()
			if not settings.clear_temp_files in bool_values:
				log_warn("Invalid or missing setting detected for 'clear_temp_files', using default value (True)")
				settings.clear_temp_files = 'true'
				has_thrown_errors = True
		except:
			log_warn("Invalid or missing setting detected for 'clear_temp_files', using default value (True)")
			settings.clear_temp_files = 'true'
			has_thrown_errors = True



		try:
			settings.save_replays = config.get('pyinstalive', 'save_replays').title()
			if not settings.save_replays in bool_values:
				log_warn("Invalid or missing setting detected for 'save_replays', using default value (True)")
				settings.save_replays = 'true'
				has_thrown_errors = True
		except:
			log_warn("Invalid or missing setting detected for 'save_replays', using default value (True)")
			settings.save_replays = 'true'
			has_thrown_errors = True

		try:
			settings.save_lives = config.get('pyinstalive', 'save_lives').title()
			if not settings.save_lives in bool_values:
				log_warn("Invalid or missing setting detected for 'save_lives', using default value (True)")
				settings.save_lives = 'true'
				has_thrown_errors = True
		except:
			log_warn("Invalid or missing setting detected for 'save_lives', using default value (True)")
			settings.save_lives = 'true'
			has_thrown_errors = True



		try:
			settings.log_to_file = config.get('pyinstalive', 'log_to_file').title()
			if not settings.log_to_file in bool_values:
				log_warn("Invalid or missing setting detected for 'log_to_file', using default value (False)")
				settings.log_to_file = 'False'
				has_thrown_errors = True
		except:
			log_warn("Invalid or missing setting detected for 'log_to_file', using default value (False)")
			settings.log_to_file = 'False'
			has_thrown_errors = True



		try:
			settings.run_at_start = config.get('pyinstalive', 'run_at_start').replace("\\", "\\\\")
			if not settings.run_at_start:
				settings.run_at_start = "None"
		except:
			log_warn("Invalid or missing settings detected for 'run_at_start', using default value (empty)")
			settings.run_at_start = "None"
			has_thrown_errors = True



		try:
			settings.run_at_finish = config.get('pyinstalive', 'run_at_finish').replace("\\", "\\\\")
			if not settings.run_at_finish:
				settings.run_at_finish = "None"
		except:
			log_warn("Invalid or missing settings detected for 'run_at_finish', using default value (empty)")
			settings.run_at_finish = "None"
			has_thrown_errors = True


		try:
			settings.save_comments = config.get('pyinstalive', 'save_comments').title()
			wide_build = sys.maxunicode > 65536
			if sys.version.split(' ')[0].startswith('2') and settings.save_comments == "True" and not wide_build:
				log_warn("Your Python 2 build does not support wide unicode characters.")
				log_warn("This means characters such as emojis will not be saved.")
				has_thrown_errors = True
			else:
				if not settings.show_cookie_expiry in bool_values:
					log_warn("Invalid or missing setting detected for 'save_comments', using default value (False)")
					settings.save_comments = 'false'
					has_thrown_errors = True
		except:
			log_warn("Invalid or missing setting detected for 'save_comments', using default value (False)")
			settings.save_comments = 'false'
			has_thrown_errors = True

		try:
			settings.save_path = config.get('pyinstalive', 'save_path')

			if (os.path.exists(settings.save_path)):
				pass
			else:
				log_warn("Invalid or missing setting detected for 'save_path', falling back to path: {:s}".format(os.getcwd()))
				settings.save_path = os.getcwd()
				has_thrown_errors = True

			if not settings.save_path.endswith('/'):
				settings.save_path = settings.save_path + '/'
		except:
			log_warn("Invalid or missing setting detected for 'save_path', falling back to path: {:s}".format(os.getcwd()))
			settings.save_path = os.getcwd()
			has_thrown_errors = True


		if has_thrown_errors:
			log_seperator()

		return True
	except Exception as e:
		print(str(e))
		return False



def show_info(config):
	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception as e:
			log_error("Could not read configuration file: {:s}".format(str(e)))
			log_seperator()
	else:
		new_config()
		sys.exit(1)

	if not check_config_validity(config):
		log_warn("Config file is not valid, some information may be inaccurate.")
		log_whiteline()

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
		log_warn("Could not check for cookie files: {:s}".format(str(e)))
		log_whiteline()
	log_info_green("To see all the available arguments, use the -h argument.")
	log_whiteline()
	log_info_green("PyInstaLive version:    	{:s}".format(script_version))
	log_info_green("Python version:         	{:s}".format(python_version))
	if not check_ffmpeg():
		log_error("FFmpeg framework:       	Not found")
	else:
		log_info_green("FFmpeg framework:       	Available")

	if (len(cookie_from_config) > 0):
		log_info_green("Cookie files:            	{:s} ({:s} matches config user)".format(str(len(cookie_files)), cookie_from_config))
	elif len(cookie_files) > 0:
		log_info_green("Cookie files:            	{:s}".format(str(len(cookie_files))))
	else:
		log_warn("Cookie files:            	None found")

	log_info_green("CLI supports color:     	{:s}".format(str(supports_color()[0])))
	log_info_green("File to run at start:       {:s}".format(settings.run_at_start))
	log_info_green("File to run at finish:      {:s}".format(settings.run_at_finish))
	log_whiteline()


	if os.path.exists('pyinstalive.ini'):
		log_info_green("Config file:")
		log_whiteline()
		with open('pyinstalive.ini') as f:
			for line in f:
				log_plain("    {:s}".format(line.rstrip()))
	else:
		log_error("Config file:	    	Not found")
	log_whiteline()
	log_info_green("End of PyInstaLive information screen.")
	log_seperator()



def new_config():
	try:
		if os.path.exists('pyinstalive.ini'):
			log_info_green("A configuration file is already present:")
			log_whiteline()
			with open('pyinstalive.ini') as f:
				for line in f:
					log_plain("    {:s}".format(line.rstrip()))
			log_whiteline()
			log_info_green("To create a default config file, delete 'pyinstalive.ini' and run this script again.")
			log_seperator()
		else:
			try:
				log_warn("Could not find configuration file, creating a default one...")
				config_template = """
[pyinstalive]
username = johndoe
password = grapefruits
save_path = {:s}
show_cookie_expiry = true
clear_temp_files = false
save_lives = true
save_replays = true
run_at_start = 
run_at_finish = 
save_comments = false
log_to_file = false
				""".format(os.getcwd())
				config_file = open("pyinstalive.ini", "w")
				config_file.write(config_template.strip())
				config_file.close()
				log_warn("Edit the created 'pyinstalive.ini' file and run this script again.")
				log_seperator()
				sys.exit(0)
			except Exception as e:
				log_error("Could not create default config file: {:s}".format(str(e)))
				log_warn("You must manually create and edit it with the following template: ")
				log_whiteline()
				for line in config_template.strip().splitlines():
					log_plain("    {:s}".format(line.rstrip()))
				log_whiteline()
				log_warn("Save it as 'pyinstalive.ini' and run this script again.")
				log_seperator()
	except Exception as e:
		log_error("An error occurred: {:s}".format(str(e)))
		log_warn("If you don't have a configuration file, manually create and edit one with the following template:")
		log_whiteline()
		log_plain(config_template)
		log_whiteline()
		log_warn("Save it as 'pyinstalive.ini' and run this script again.")
		log_seperator()



def clean_download_dir():
	dir_delcount = 0
	error_count = 0
	lock_count = 0

	log_info_green('Cleaning up temporary files and folders...')
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
						log_error("Could not remove temp folder: {:s}".format(str(e)))
						error_count += 1
				else:
					lock_count += 1
		log_seperator()
		log_info_green('The cleanup has finished.')
		if dir_delcount == 0 and error_count == 0 and lock_count == 0:
			log_info_green('No folders were removed.')
			log_seperator()
			return
		log_info_green('Folders removed:     {:d}'.format(dir_delcount))
		log_info_green('Locked folders:      {:d}'.format(lock_count))
		log_info_green('Errors:              {:d}'.format(error_count))
		log_seperator()
	except KeyboardInterrupt as e:
		log_seperator()
		log_warn("The cleanup has been aborted.")
		if dir_delcount == 0 and error_count == 0 and lock_count == 0:
			log_info_green('No folders were removed.')
			log_seperator()
			return
		log_info_green('Folders removed:     {:d}'.format(dir_delcount))
		log_info_green('Locked folders:      {:d}'.format(lock_count))
		log_info_green('Errors:              {:d}'.format(error_count))
		log_seperator()

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
	parser.add_argument('-nl', '--nolives', dest='nolives', action='store_true', help="When used, do not check for any available livestreams.")
	parser.add_argument('-cl', '--clean', dest='clean', action='store_true', help="PyInstaLive will clean the current download folder of all leftover files.")
	parser.add_argument('-df', '--downloadfollowing', dest='downloadfollowing', action='store_true', help="PyInstaLive will check for available livestreams and replays from users the account used to login follows.")


	# Workaround to 'disable' argument abbreviations
	parser.add_argument('--usernamx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--passworx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--recorx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--infx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--confix', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--noreplayx', help=argparse.SUPPRESS, metavar='IGNORE') 
	parser.add_argument('--cleax', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('--downloadfollowinx', help=argparse.SUPPRESS, metavar='IGNORE')

	parser.add_argument('-cx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('-nx', help=argparse.SUPPRESS, metavar='IGNORE')
	parser.add_argument('-dx', help=argparse.SUPPRESS, metavar='IGNORE')



	args, unknown_args = parser.parse_known_args()


	try:
		config.read('pyinstalive.ini')
		settings.log_to_file = config.get('pyinstalive', 'log_to_file').title()
		if not settings.log_to_file in bool_values:
			settings.log_to_file = 'False'
		elif settings.log_to_file == "True":
			if args.download:
				settings.user_to_download = args.download
			try:
				with open("pyinstalive{:s}.log".format("_" + settings.user_to_download if len(settings.user_to_download) > 0 else ".default"),"a+") as f:
					f.write("\n")
					f.close()
			except:
				pass
	except Exception as e:
		settings.log_to_file = 'False'
		pass # Pretend nothing happened

	log_seperator()
	log_info_blue('PYINSTALIVE (SCRIPT V{:s} - PYTHON V{:s}) - {:s}'.format(script_version, python_version, time.strftime('%I:%M:%S %p')))
	log_seperator()

	if unknown_args:
		log_error("The following invalid argument(s) were provided: ") 
		log_whiteline() 
		log_info_blue('    ' + ' '.join(unknown_args)) 
		log_whiteline()
		if (supports_color()[1] == True):
			log_info_green("'pyinstalive -h' can be used to display command help.")
		else:
			log_plain("pyinstalive -h can be used to display command help.")
		log_seperator()
		exit(1)

	if (args.info) or (not
	args.username and not
	args.password and not
	args.download and not
	args.downloadfollowing and not
	args.info and not
	args.config and not
	args.noreplays and not
	args.nolives and not
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
			log_error("Could not read configuration file.")
			log_seperator()
	else:
		new_config()
		sys.exit(1)


	if check_config_validity(config):
		try:
			if (args.clean):
				clean_download_dir()
				sys.exit(0)

			if not check_ffmpeg():
				log_error("Could not find ffmpeg, the script will now exit. ")
				log_seperator()
				sys.exit(1)

			if (args.noreplays):
				settings.save_replays = "False"

			if (args.nolives):
				settings.save_lives = "False"

			if settings.save_lives == "False" and settings.save_replays == "False":
				log_warn("Script will not run because both live and replay saving is disabled.")
				log_seperator()
				sys.exit(1)

			if not args.download and not args.downloadfollowing:
				log_warn("Neither argument -d or -df was passed. Please use one of the two and try again.")
				log_seperator()
				sys.exit(1)

			if args.download and args.downloadfollowing:
				log_warn("You can't pass both the -d and -df arguments. Please use one of the two and try again.")
				log_seperator()
				sys.exit(1)


			if (args.username is not None) and (args.password is not None):
				api = login(args.username, args.password, settings.show_cookie_expiry, True)
			elif (args.username is not None) or (args.password is not None):
				log_warn("Missing --username or --password argument, falling back to configuration file...")
				if (not len(settings.username) > 0) or (not len(settings.password) > 0):
					log_error("Username or password are missing. Please check your configuration file and try again.")
					log_seperator()
					sys.exit(1)
				else:
					api = login(settings.username, settings.password, settings.show_cookie_expiry, False)
			else:
				if (not len(settings.username) > 0) or (not len(settings.password) > 0):
					log_error("Username or password are missing. Please check your configuration file and try again.")
					log_seperator()
					sys.exit(1)
				else:
					api = login(settings.username, settings.password, settings.show_cookie_expiry, False)
			if args.download and not args.downloadfollowing:
				start_single(api, args.download, settings)
			if not args.download and args.downloadfollowing:
				if check_pyinstalive():
					start_multiple(api, settings, "pyinstalive")
				else:
					log_warn("You probably ran PyInstaLive as a script module with the -m argument.")
					log_warn("PyInstaLive should be properly installed when using the -df argument.")
					log_seperator()
					if python_version[0] == "3":
						start_multiple(api, settings, "python3 -m pyinstalive")
					else:
						start_multiple(api, settings, "python -m pyinstalive")
		except Exception as e:
			log_error("Could not finish pre-download checks:  {:s}".format(str(e)))
			log_seperator()
		except KeyboardInterrupt as ee:
			log_warn("Pre-download checks have been aborted, exiting...")
			log_seperator()

	else:
		log_error("The configuration file is not valid. Please double-check and try again.")
		log_seperator()
		sys.exit(1)