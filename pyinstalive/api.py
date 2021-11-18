from datetime import datetime
import json
from json.decoder import JSONDecodeError

from . import helpers
from . import globals
from . import logger
from .constants import Constants

def get_csrf_token():
    response = globals.session.session.get(Constants.LOGIN_PAGE)
    result = helpers.get_shared_data(response.text)["config"]["csrf_token"]
    return result

def do_login():
    now_epoch = int(datetime.now().timestamp())
    login_data = {"username": globals.session.username, "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{now_epoch}:{globals.session.password}", "queryParams": {}, "optIntoOneTap": "false"}
    login_response = globals.session.session.post(Constants.LOGIN_AJAX, data=login_data)
    result = json.loads(login_response.text)
    return result

def get_login_state():
    login_response = globals.session.session.get(Constants.BASE_WEB)
    result = helpers.get_shared_data(login_response.text)
    return result

def get_broadcasts_tray():
    response = globals.session.session.get(Constants.REELS_TRAY)
    response_json = json.loads(response.text)
    return response_json

def get_comments():
    comments_response = globals.session.session.get(Constants.LIVE_COMMENT.format(globals.download.livestream_object_init.get('broadcast_id'), str(globals.comments.comments_last_ts)))
    comments_json = json.loads(comments_response.text)
    return comments_json

def get_stream_data():
    response = globals.session.session.get(Constants.LIVE_INFO.format(globals.download.livestream_object_init.get('broadcast_id')))
    response_json = json.loads(response.text)
    return response_json

def no_heartbeat():
    globals.session.session.post(Constants.LIVE_HEARTBEAT.format(globals.download.livestream_object_init.get('broadcast_id')))