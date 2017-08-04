import json
import codecs
import datetime
import os.path
import logging
import argparse
import json
import codecs
from socket import timeout, error as SocketError
from ssl import SSLError
from urllib2 import URLError
from httplib import HTTPException

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

from instagram_private_api_extensions import live
import sys, os, time, json

def download():
    try:
        user_res = api.username_info(args.record)
        user_id = user_res['user']['pk']
    except Exception as e:
        print('[E] Could not get user information, exiting . . .')
        print('[E] ' + str(e))
        print(seperator)
        exit()

    try:
        print('[I] Checking broadcast for ' + args.record + ' . . .')
        broadcast = api.user_broadcast(user_id)
        if (broadcast is None):
            raise Exception('No broadcast available')
    except Exception as e:
        print('[E] Could not get broadcast information, exiting . . .')
        print('[E] ' + str(e))
        print(seperator)
        exit()

    try:
        dl = live.Downloader(
            mpd=broadcast['dash_playback_url'],
            output_dir='{}_output_{}/'.format(args.record, broadcast['id']),
            user_agent=api.user_agent)
    except Exception as e:
        print('[E] Could not start broadcast recording, exiting . . .')
        print('[E] ' + str(e))
        print(seperator)
        exit()

    try:
        print('[I] Starting broadcast recording . . .')
        dl.run()
    except KeyboardInterrupt:
        print('')
        print('[I] Aborting broadcast recording . . .')
        if not dl.is_aborted:
            dl.stop()
    finally:
        t = time.time()
        print('[I] Stitching downloaded files into video . . .')
        dl.stitch(args.record + "_" + str(broadcast['id']) + "_" + str(int(t)) + '.mp4')
        print('[I] Successfully stitched downloaded files, exiting . . .')
        print(seperator)
        exit()

def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))


if __name__ == '__main__':

    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    # python examples/savesettings_logincallback.py -u "yyy" -p "zzz" -settings "test_credentials.json"
    parser = argparse.ArgumentParser(description='login callback and save settings demo')
    parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    parser.add_argument('-r', '--record', dest='record', type=str, required=True)
    global args
    global clear
    global seperator
    seperator = '=-' * 35
    clear = lambda: os.system('clear')
    args = parser.parse_args()
    #clear()
    print('PYINSTALIVE DOWNLOADER (API v{0!s})'.format(client_version))
    print(seperator)

    device_id = None
    try:

        settings_file = args.settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            print('[E] Unable to find file: {0!s}'.format(settings_file))

            # login new
            api = Client(
                args.username, args.password,
                on_login=lambda x: onlogin_callback(x, args.settings_file_path))
        else:
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            print('[I] Reusing settings: {0!s}'.format(settings_file))

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            api = Client(
                args.username, args.password,
                settings=cached_settings)

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('[E] ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        api = Client(
            args.username, args.password,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, args.settings_file_path))

    except ClientLoginError as e:
        print('[E] ClientLoginError {0!s}'.format(e))
        print(seperator)
        exit(9)
    except ClientError as e:
        print('[E] ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
        print(seperator)
        exit(9)
    except Exception as e:
        print('[E] Unexpected Exception: {0!s}'.format(e))
        print(seperator)
        exit(99)

    # Show when login expires
    cookie_expiry = api.cookie_jar.expires_earliest
    print('[I] Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

print('[I] Successfully logged in, starting recorder . . .')
download()