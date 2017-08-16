import argparse
import logging
import os.path
import configparser
import sys
import auth, downloader, logger


def run():

	scriptVersion = "2.1.4"

    logger.log('PYINSTALIVE DOWNLOADER (SCRIPT v{0!s})'.format(scriptVersion), "GREEN")
    logger.seperator("GREEN")

	logging.disable(logging.CRITICAL)
	config = configparser.ConfigParser()

	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception as e:
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
		api = auth.login(args.username, args.password)
	else:
		api = auth.login(config['pyinstalive']['username'], config['pyinstalive']['password'])
	
	savePath = config['pyinstalive']['save_path']
	if not savePath.endswith('/'):
		savePath = savePath + '/'

	if (os.path.exists(savePath)):
		downloader.main(api, args.record, savePath)
	else:
		logger.log("[W] Invalid save path was specified! Falling back to location: " + os.getcwd(), "RED")
		downloader.main(api, args.record, os.getcwd())