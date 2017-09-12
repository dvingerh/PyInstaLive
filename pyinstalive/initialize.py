import argparse
import configparser
import logging
import os.path
import sys

import auth, downloader, logger

def check_config_validity(config):
	username = config['pyinstalive']['username']
	password = config['pyinstalive']['password']

	if not (len(username) > 0):
		logger.log("[E] Invalid setting detected for 'username'.", "RED")
		return False

	if not (len(password) > 0):
		logger.log("[E] Invalid setting detected for 'password'.", "RED")
		return False

	return True


def run():

	script_version = "2.2.0"
	bool_values = {'True', 'False'}

	logger.log('PYINSTALIVE DOWNLOADER (SCRIPT v{0!s})'.format(script_version), "GREEN")
	logger.seperator("GREEN")

	logging.disable(logging.CRITICAL)
	config = configparser.ConfigParser()

	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception:
			logger.log("[E] Could not read configuration file. Try passing the required arguments manually.", "RED")
			logger.seperator("GREEN")
	else:
		logger.log("[W] Could not find configuration file, creating a default one ...", "YELLOW")
		try:
			config_template = "[pyinstalive]\nusername = johndoe\npassword = grapefruits\nsave_path = /\nshow_cookie_expiry = true"
			config_file = open("pyinstalive.ini", "w")
			config_file.write(config_template)
			config_file.close()
			logger.log("[W] Edit the created 'pyinstalive.ini' file and run this script again.", "YELLOW")
			logger.seperator("GREEN")
			sys.exit(0)
		except Exception as e:
			logger.log("[E] Could not create default config file: " + str(e), "RED")
			logger.log("[W] You must manually create and edit it with the following template: ", "YELLOW")
			logger.log("", "GREEN")
			logger.log(config_template, "BLUE")
			logger.log("", "GREEN")
			logger.log("[W] Save it as 'pyinstalive.ini' and run this script again.", "YELLOW")
			logger.log("", "GREEN")
			sys.exit(1)


	parser = argparse.ArgumentParser(description='Login')
	parser.add_argument('-u', '--username', dest='username', type=str, required=False)
	parser.add_argument('-p', '--password', dest='password', type=str, required=False)
	parser.add_argument('-r', '--record', dest='record', type=str, required=True)

	args = parser.parse_args()

	if check_config_validity(config):

		username = config['pyinstalive']['username']
		password = config['pyinstalive']['password']

		try:
			show_cookie_expiry = config['pyinstalive']['show_cookie_expiry']
			if not config['pyinstalive']['show_cookie_expiry'].title() in bool_values:
				logger.log("[W] Invalid setting detected for 'show_cookie_expiry', falling back to default value (True)", "YELLOW")
				show_cookie_expiry = 'True'
		except:
			logger.log("[W] Invalid setting detected for 'show_cookie_expiry', falling back to default value (True)", "YELLOW")
			show_cookie_expiry = 'True'

		try:
			save_path = config['pyinstalive']['save_path']

			if (os.path.exists(save_path)):
				pass
			else:
				logger.log("[W] Invalid setting detected for 'save_path', falling back to location: " + os.getcwd(), "YELLOW")
				save_path = os.getcwd()

			if not save_path.endswith('/'):
				save_path = save_path + '/'
		except:
			logger.log("[W] Invalid setting detected for 'save_path', falling back to location: " + os.getcwd(), "YELLOW")
			save_path = os.getcwd()

		if (args.username is not None) and (args.password is not None):
			api = auth.login(args.username, args.password, show_cookie_expiry)
		else:
			api = auth.login(username, password, show_cookie_expiry)
		
		downloader.main(api, args.record, save_path)
	else:
		logger.log("[E] The configuration file is not valid. Please check your configuration settings and try again.", "RED")
		logger.seperator("GREEN")
		sys.exit(0)
