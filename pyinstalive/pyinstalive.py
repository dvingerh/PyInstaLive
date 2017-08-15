import argparse
import logging
import os.path
import configparser
import sys
import auth, downloader, logger


def run():
	logging.disable(logging.CRITICAL)
	config = configparser.ConfigParser()

	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception as e:
			logger.log("[E] Could not read configuration file! Try passing the required arguments manually.", "RED")
	else:
		logger.log("[E] Could not find configuration file! Exiting...", "RED")
		sys.exit(0)


	parser = argparse.ArgumentParser(description='Login')
	parser.add_argument('-u', '--username', dest='username', type=str, required=False)
	parser.add_argument('-p', '--password', dest='password', type=str, required=False)
	parser.add_argument('-r', '--record', dest='record', type=str, required=True)

	args = parser.parse_args()

	if (args.username is not None) and (args.password is not None):
		api = auth.login(args.username, args.password)
	else:
		api = auth.login(config['pyinstalive']['username'], config['pyinstalive']['password'])

	if (os.path.exists(config['pyinstalive']['save_path'])):
		downloader.main(api, args.record, config['pyinstalive']['save_path'])
	else:
		logger.log("[W] Invalid save path was specified! Falling back to location: " + os.getcwd(), "RED")
		downloader.main(api, args.record, os.getcwd())