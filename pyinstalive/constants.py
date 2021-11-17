import sys


class Constants:
    SCRIPT_VERSION = "4.0.0"
    PYTHON_VERSION = sys.version.split(" ")[0]
    CONFIG_TEMPLATE = """
[pyinstalive]
username = johndoe
password = grapefruits
download_path = {:s}
show_session_expires = True
download_comments = True
clear_temp_files = False
cmd_on_started =
cmd_on_ended =
ffmpeg_path = 
log_to_file = True
no_assemble = False
use_locks = True
    """



    BASE_HEADERS =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', "x-ig-app-id": '936619743392459'}
    BASE_WEB = "https://www.instagram.com/"
    BASE_API = "https://i.instagram.com/api/v1/"

    LOGIN_PAGE = BASE_WEB + "accounts/login/"
    LOGIN_AJAX = BASE_WEB + "accounts/login/ajax/"

    REELS_TRAY = BASE_API + "live/reels_tray_broadcasts/"
    LIVE_INFO = BASE_API + "live/{:s}/info/"
    LIVE_STATE_USER = BASE_WEB + "{:s}/live/?__a=1"
    LIVE_HEARTBEAT = BASE_API + "live/{:s}/heartbeat_and_get_viewer_count/"
    LIVE_COMMENT = BASE_API + "live/{:s}/get_comment/?last_comment_ts={:s}"
