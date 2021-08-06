import codecs
import datetime
import json
import os.path
import sys
import traceback
import requests
import json
from datetime import datetime
import os
import re
import pickle
try:
    import logger
    import pil
    from constants import Constants
except ImportError:
    from . import logger
    from . import pil
    from .constants import Constants


def get_shared_data(html):
    match = re.search(r'window._sharedData = ({[^\n]*});', html)
    return json.loads(match.group(1))

def save_session(session, filename):
    with open(filename, 'wb') as f:
        pickle.dump(session, f)

def load_session(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def authenticate(username, password, force_use_login_args=False):
    ig_api = None
    try:
        if force_use_login_args:
            pil.ig_user = username
            pil.ig_pass = password
            pil.config_login_overridden = True
            logger.binfo("Overriding configuration file login with -u and -p arguments.")
            logger.separator()
        session_file = os.path.join(os.path.dirname(pil.config_path), "{}.dat".format(username))
        if not os.path.isfile(session_file):
            # settings file does not exist
            logger.warn('Unable to find login session file: {0!s}'.format(os.path.basename(session_file)))
            logger.info('A new login session file will be created after logging in.')
            logger.separator()

            # login new
            session = requests.session()
            session.headers = Constants.LOGIN_HEADERS
            response = session.get(Constants.LOGIN_URL)
            csrf = get_shared_data(response.text)['config']['csrf_token']
            cur_time = int(datetime.now().timestamp())
            payload = {'username': username,
                    'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{cur_time}:{password}',
                    'queryParams': {},
                    'optIntoOneTap': 'false'}

                            
            session.headers.update({"x-csrftoken": csrf})
            login_response = session.post(Constants.LOGIN_URL_AJAX, data=payload)
            json_data = json.loads(login_response.text)
            if json_data.get("authenticated") == True:
                save_session(session, session_file)
                ig_api = session
                logger.binfo('New login session file was created: {0!s}'.format(os.path.basename(session_file)))
                logger.separator()
            else:
                logger.error('Could not login, ensure your credentials are correct and try again.')
                logger.separator()
                ig_api = None
        else:
            ig_api = load_session(session_file)
            logger.info("Using login session file: {0!s}".format(os.path.basename(session_file)))

    except Exception as e:
        logger.error('Unexpected exception: {:s}'.format(e))
        logger.separator()
    except KeyboardInterrupt:
        logger.separator()
        logger.warn("The user authentication has been aborted.")
        logger.separator()

    if ig_api:
        logger.info('Successfully logged into account: {:s}'.format(str(username)))
        expiry_epoch = 0
        for cookie in list(ig_api.cookies):
            if cookie.name == "csrftoken":
                expiry_epoch = cookie.expires
        if ig_api.cookies["csrftoken"] != ig_api.headers.get("x-csrftoken"):
            ig_api.cookies.set("csrftoken", ig_api.headers.get("x-csrftoken"), domain=".instagram.com", expires=expiry_epoch)
        if pil.show_cookie_expiry:
            cookie_expiry_date = datetime.fromtimestamp(expiry_epoch).strftime('%Y-%m-%d at %I:%M:%S %p')
            logger.separator()
            logger.info("Login session file expiry date: {}".format(cookie_expiry_date))
            logger.separator()
        return ig_api
    else:
        return None
