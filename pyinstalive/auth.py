import codecs
import datetime
import json
import os.path
import sys
from .logger import log, seperator



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
	if '__class__' in json_object and json_object['__class__'] == 'bytes':
		return codecs.decode(json_object['__value__'].encode(), 'base64')
	return json_object


def onlogin_callback(api, settings_file):
	cache_settings = api.settings
	with open(settings_file, 'w') as outfile:
		json.dump(cache_settings, outfile, default=to_json)
		log('[I] New auth cookie file was made: {0!s}'.format(settings_file), "GREEN")


def login(username, password, show_cookie_expiry, ignore_existing_cookie):
	device_id = None
	try:
		if ignore_existing_cookie:
			api = Client(
				username, password)
		else:
			settings_file = username + ".json"
			if not os.path.isfile(settings_file):
				# settings file does not exist
				log('[W] Unable to find auth cookie file: {0!s}'.format(settings_file), "YELLOW")

				# login new
				api = Client(
					username, password,
					on_login=lambda x: onlogin_callback(x, settings_file))
			else:
				with open(settings_file) as file_data:
					cached_settings = json.load(file_data, object_hook=from_json)
				# log('[I] Using settings file: {0!s}'.format(settings_file), "GREEN")

				device_id = cached_settings.get('device_id')
				# reuse auth settings
				api = Client(
					username, password,
					settings=cached_settings)

	except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
		log('[E] ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e), "RED")

		# Login expired
		# Do relogin but use default ua, keys and such
		api = Client(
			username, password,
			device_id=device_id,
			on_login=lambda x: onlogin_callback(x, settings_file))

	except ClientLoginError as e:
		log('[E] ClientLoginError: {0!s}\n\n(Code: {1:d}, Response: {2!s})\n'.format(e.msg, e.code, e.error_response), "RED")
		seperator("GREEN")
		sys.exit(9)
	except ClientError as e:
		log('[E] ClientError: {0!s}\n\n(Code: {1:d}, Response: {2!s})\n'.format(e.msg, e.code, e.error_response), "RED")
		seperator("GREEN")
		sys.exit(9)
	except Exception as e:
		if (str(e).startswith("unsupported pickle protocol")):
			log("[W] This cookie file is not compatible with Python {}.".format(sys.version.split(' ')[0][0]), "YELLOW")
			log("[W] Please delete your cookie file '" + username + ".json' and try again.", "YELLOW")
		else:
			log('[E] Unexpected Exception: {0!s}'.format(e), "RED")
		seperator("GREEN")
		sys.exit(99)

	log('[I] Login to "' + api.authenticated_user_name + '" OK!', "GREEN")
	if show_cookie_expiry.title() == 'True' and ignore_existing_cookie == False:
		cookie_expiry = api.cookie_jar.expires_earliest
		log('[I] Login cookie expiry date: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%d at %H:%M:%S')), "GREEN")

	return api