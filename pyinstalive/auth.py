import codecs
import datetime
import json
import os.path
import sys
import traceback
import time
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
            logger.binfo("Overriding configuration file login using arguments.")
            logger.separator()
        session_file = os.path.join(os.path.dirname(pil.config_path), "{}.dat".format(username))
        if not os.path.isfile(session_file):
            logger.warn('Could not find existing login session file: {0!s}'.format(os.path.basename(session_file)))
            logger.info('A new login session file will be created upon successful login.')

            expiry_epoch = 0
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
            login_response = session.post(Constants.AJAX_LOGIN_URL, data=payload)
            json_data = json.loads(login_response.text)
            if json_data.get("authenticated") == True:
                save_session(session, session_file)
                logger.info('Successfully created a new login session file.')
                ig_api = session
                for cookie in list(ig_api.cookies):
                    if cookie.name == "csrftoken":
                        expiry_epoch = cookie.expires
            else:
                logger.separator()
                if (json_data.get("message") == 'checkpoint_required'):
                    logger.error('Could not login. The action was flagged as suspicious by Instagram.')
                    logger.error('Please complete the security checkpoint and try again.')
                else:
                    logger.error('Could not login. Ensure your credentials are correct and try again.')
                logger.separator()
                ig_api = None
        else:
            logger.info("An existing login session file was found: {0!s}".format(os.path.basename(session_file)))
            logger.info("Checking the validity of the saved login session.")
            ig_api = load_session(session_file)
            for cookie in list(ig_api.cookies):
                if cookie.name == "csrftoken":
                    expiry_epoch = cookie.expires
            if int(expiry_epoch) <= int(pil.epochtime):
                os.remove(session_file)
                logger.separator()
                logger.warn('The login session file has expired and has been deleted.')
                logger.warn('A new login attempt will be made in a few moments.')
                logger.separator()
                time.sleep(2.5)
                authenticate(username, password)
                return ig_api
            else:
                response = ig_api.get(Constants.MAIN_SITE_URL)
                login_state = get_shared_data(response.text)
                if login_state.get("entry_data").get("FeedPage", None) == None:
                    if login_state.get("entry_data").get("Challenge", None) != None:
                        logger.error("The login session file is no longer valid.")
                        logger.error('The session was flagged as suspicious by Instagram.')
                        logger.error('Please complete the security checkpoint and try again.')
                        logger.separator()
                        ig_api = None
                    else:
                        logger.error("The login session file is no longer valid.")
                        logger.error('Unspecified error. Please delete the login session file and try again.')
                        logger.separator()
                        ig_api = None

    except Exception as e:
        logger.separator()
        logger.error('Could not login due to an error: {:s}'.format(e))
        logger.separator()
        return None
    except KeyboardInterrupt:
        logger.separator()
        logger.binfo("The login was aborted by the user.")
        logger.separator()
        return None

    if ig_api:
        if ig_api.cookies["csrftoken"] != ig_api.headers.get("x-csrftoken"):
            ig_api.cookies.set("csrftoken", ig_api.headers.get("x-csrftoken"), domain=".instagram.com", expires=expiry_epoch)
        logger.separator()
        logger.info('Successfully logged in using account: {:s}'.format(str(username)))
        if pil.show_session_expires:
            expiry_date = datetime.fromtimestamp(expiry_epoch).strftime('%m-%d-%Y at %I:%M:%S %p')
            logger.info("The login session file will expire on: {:s}".format(expiry_date))
        logger.separator()
        return ig_api
    else:
        return None
