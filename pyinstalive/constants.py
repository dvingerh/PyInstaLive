import sys


class Constants:
    SCRIPT_VERSION = "4.0.0"
    PYTHON_VERSION = sys.version.split(" ")[0]
    CONFIG_TEMPLATE = """
[pyinstalive]
username = johndoe
password = grapefruits
download_path = {:s}
ffmpeg_path = 
download_comments = True    
cmd_on_started =
cmd_on_ended =
clear_temp_files = False
use_locks = True
no_assemble = False
log_to_file = True
    """



    BASE_HEADERS =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36', "x-ig-app-id": '936619743392459'}
    BASE_WEB = "https://www.instagram.com/"
    BASE_API = "https://i.instagram.com/api/v1/"

    LOGIN_PAGE = BASE_WEB + "accounts/login/"
    LOGIN_AJAX = BASE_WEB + "accounts/login/ajax/"

    REELS_TRAY = BASE_API + "live/reels_tray_broadcasts/"
    USER_INFO = BASE_API + "users/web_profile_info/?username={:s}"
    LIVE_STATE_USER = BASE_API + "live/web_info/?target_user_id={:s}"
    LIVE_HEARTBEAT = BASE_API + "live/{:s}/heartbeat_and_get_viewer_count/"
    LIVE_COMMENT = BASE_API + "live/{:s}/get_comment/?last_comment_ts={:s}"
