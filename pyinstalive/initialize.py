import argparse
import configparser
import logging
import os.path
import sys

import auth, downloader, logger


def run():

	script_version = "2.1.6"

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

	if (args.username is not None) and (args.password is not None):
		api = auth.login(args.username, args.password, config['pyinstalive']['show_cookie_expiry'].title())
	else:
		api = auth.login(config['pyinstalive']['username'], config['pyinstalive']['password'], config['pyinstalive']['show_cookie_expiry'].title())
	
	save_path = config['pyinstalive']['save_path']
	if not save_path.endswith('/'):
		save_path = save_path + '/'

	if (os.path.exists(save_path)):
		downloader.main(api, args.record, save_path)
	else:
		logger.log("[W] Invalid save path was specified! Falling back to location: " + os.getcwd(), "RED")
		downloader.main(api, args.record, os.getcwd())