from datetime import datetime
import json

from . import helpers
from . import globals
from .constants import Constants

def get_csrf_token():
    response = globals.session.session.get(Constants.LOGIN_PAGE)
    return helpers.get_shared_data(response.text).get("config", None).get("csrf_token", None)

def do_login():
    now_epoch = int(datetime.now().timestamp())
    login_data = {
    "username": globals.session.username,
    "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{now_epoch}:{globals.session.password}",
    "queryParams": {},
    "optIntoOneTap": "false"
    }
    response = globals.session.session.post(Constants.LOGIN_AJAX, data=login_data, timeout=5)
    return json.loads(response.text)

def get_login_state():
    response = globals.session.session.get(Constants.BASE_WEB, timeout=5)
    return helpers.get_shared_data(response.text)

def get_user_info():
    response = globals.session.session.get(Constants.USER_INFO.format(globals.download.download_user), timeout=5)
    return json.loads(response.text) if response.status_code == 200 else {}

def get_reels_tray():
    response = globals.session.session.get(Constants.REELS_TRAY, timeout=5)
    return json.loads(response.text)

def get_single_live():
    response = globals.session.session.get(Constants.LIVE_STATE_USER.format(globals.download.download_user_id), timeout=5)
    return json.loads(response.text)

def get_comments():
    response = globals.session.session.get(Constants.LIVE_COMMENT.format(globals.download.livestream_object_init.get('id'), str(globals.comments.comments_last_ts)), timeout=5)
    return json.loads(response.text)

def get_stream_data():
    response = globals.session.session.get(Constants.LIVE_STATE_USER.format(globals.download.download_user_id), timeout=5)
    return json.loads(response.text)

def do_heartbeat():
    response = globals.session.session.post(Constants.LIVE_HEARTBEAT.format(globals.download.livestream_object_init.get('id')), timeout=5)
    return json.loads(response.text)
