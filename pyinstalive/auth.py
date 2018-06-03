import codecs
import datetime
import json
import os.path
import sys

from .logger import log
from .logger import seperator



try:
	from instagram_private_api import (
		Client, ClientError, ClientLoginError,
		ClientCookieExpiredError, ClientLoginRequiredError)
except ImportError:
	import sys
	sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
	from instagram_private_api import (
		Client, ClientError, ClientLoginError,
		ClientCookieExpiredError, ClientLoginRequiredError)


def to_json(python_object):
	if isinstance(python_object, bytes):
		return {'__class__': 'bytes',
				'__value__': codecs.encode(python_object, 'base64').decode()}
	raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
	if '__class__' in json_object and json_object.get('__class__') == 'bytes':
		return codecs.decode(json_object.get('__value__').encode(), 'base64')
	return json_object


def onlogin_callback(api, cookie_file):
	cache_settings = api.settings
	with open(cookie_file, 'w') as outfile:
		json.dump(cache_settings, outfile, default=to_json)
		log('[I] New cookie file was made: {0!s}'.format(cookie_file), "GREEN")
		seperator("GREEN")


def login(username, password, show_cookie_expiry, force_use_login_args):
	device_id = None
	try:
		if force_use_login_args:
			log("[I] Overriding standard login with -u and -p arguments...", "GREEN")
			api = Client(
				username, password)
		else:
			cookie_file = "{}.json".format(username)
			if not os.path.isfile(cookie_file):
				# settings file does not exist
				log('[W] Unable to find cookie file: {0!s}'.format(cookie_file), "YELLOW")
				log('[I] Creating a new cookie file...', "YELLOW")

				# login new
				api = Client(
					username, password,
					on_login=lambda x: onlogin_callback(x, cookie_file))
			else:
				with open(cookie_file) as file_data:
					cached_settings = json.load(file_data, object_hook=from_json)
				# log('[I] Using settings file: {0!s}'.format(cookie_file), "GREEN")

				device_id = cached_settings.get('device_id')
				# reuse auth cached_settings
				api = Client(
					username, password,
					settings=cached_settings)

	except (ClientCookieExpiredError) as e:
		log('[W] The current cookie file for "{:s}" has expired, creating a new one...'.format(username), "YELLOW")

		# Login expired
		# Do relogin but use default ua, keys and such
		try:
			api = Client(
				username, password,
				device_id=device_id,
				on_login=lambda x: onlogin_callback(x, cookie_file))
		except Exception as ee:
			seperator("GREEN")
			log('[E] An error occurred while trying to create a new cookie file: {:s}'.format(str(ee)), "RED")
			if "getaddrinfo failed" in str(ee):
				log('[E] Could not resolve host, check your internet connection.', "RED")
			elif "timed out" in str(ee):
				log('[E] The connection timed out, check your internet connection.', "RED")
			elif "bad_password" in str(ee):
				log('[E] The password you entered is incorrect. Please try again.', "RED")
			else:
				log('[E] {:s}'.format(ee.message), "RED")
			seperator("GREEN")
			exit(1)

	except ClientLoginError as e:
		seperator("GREEN")
		log('[E] Could not login: {:s}.\n[E] {:s}\n\n{:s}'.format(json.loads(e.error_response).get("error_title", "Error title not available."), json.loads(e.error_response).get("message", "Not available"), e.error_response), "RED")
		seperator("GREEN")
		sys.exit(9)
	except ClientError as e:
		seperator("GREEN")
		try:
			log('[E] Unexpected exception: {0!s}\n[E] Message: {1!s}\n[E] Code: {2:d}\n\n[E] Full response:\n{3!s}\n'.format(e.msg, json.loads(e.error_response).get("message", "Additional error information not available."), e.code, e.error_response), "RED")
		except Exception as ee:
			log('[E] An error occurred while trying to handle a previous exception.\n[E] 1: {:s}\n[E] 2: {:s}'.format(str(e), str(ee)), "RED")
			if "getaddrinfo failed" in str(ee):
				log('[E] Could not resolve host, check your internet connection.', "RED")
			if "timed out" in str(ee):
				log('[E] The connection timed out, check your internet connection.', "RED")
		seperator("GREEN")
		sys.exit(9)
	except Exception as e:
		if (str(e).startswith("unsupported pickle protocol")):
			log("[W] This cookie file is not compatible with Python {}.".format(sys.version.split(' ')[0][0]), "YELLOW")
			log("[W] Please delete your cookie file '{}.json' and try again.".format(username), "YELLOW")
		else:
			seperator("GREEN")
			log('[E] Unexpected exception: {0!s}'.format(e), "RED")
		seperator("GREEN")
		sys.exit(99)
	except KeyboardInterrupt as e:
		seperator("GREEN")
		log("[W] The user authentication has been aborted.", "YELLOW")
		seperator("GREEN")
		sys.exit(0)

	log('[I] Successfully logged into user "{:s}".'.format(str(api.authenticated_user_name)), "GREEN")
	if show_cookie_expiry.title() == 'True' and not force_use_login_args:
		try:
			cookie_expiry = api.cookie_jar.auth_expires
			log('[I] Cookie file expiry date: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%d at %I:%M:%S %p')), "GREEN")
		except AttributeError as e:
			log('[W] An error occurred while getting the cookie file expiry date: {0!s}'.format(e), "YELLOW")

	seperator("GREEN")		
	return api