import argparse
import configparser
import logging
import os.path
import sys

import auth, downloader, logger

def check_config_validity(config):
	username = config['pyinstalive']['username']
	password = config['pyinstalive']['password']

	if not ((len(username) > 0) or (len(password) > 0)):
		logger.log("[E] Username or password are not entered correct in config file!", "RED")
		return False

	return True


def run():

	script_version = "2.1.8"
	bool_values = {'True', 'False'}

	logger.log('PYINSTALIVE DOWNLOADER (SCRIPT v{0!s})'.format(script_version), "GREEN")
	logger.seperator("GREEN")

	logging.disable(logging.CRITICAL)
	config = configparser.ConfigParser()

	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception:
			logger.log("[E] Could not read configuration file! Try passing the required arguments manually.", "RED")
			logger.seperator("GREEN")
	else:
		logger.log("[E] Could not find configuration file!", "RED")
		logger.seperator("GREEN")
		sys.exit(0)


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
				logger.log("[W] Invalid setting detected for show_cookie_expiry, falling back to default value (True)", "YELLOW")
				show_cookie_expiry = 'True'
		except:
			logger.log("[W] Invalid setting detected for show_cookie_expiry, falling back to default value (True)", "YELLOW")
			show_cookie_expiry = 'True'

		try:
			save_path = config['pyinstalive']['save_path']

			if (os.path.exists(save_path)):
				pass
			else:
				logger.log("[W] Invalid setting detected for save_path, falling back to location: " + os.getcwd(), "YELLOW")
				save_path = os.getcwd()

			if not save_path.endswith('/'):
				save_path = save_path + '/'
		except:
			logger.log("[W] Invalid setting detected for save_path, falling back to location: " + os.getcwd(), "YELLOW")
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
