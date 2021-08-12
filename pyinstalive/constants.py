import sys


class Constants:
    SCRIPT_VER = "3.3.0"
    PYTHON_VER = sys.version.split(' ')[0]
    CONFIG_TEMPLATE = """
[pyinstalive]
username = johndoe
password = grapefruits
download_path = {:s}
show_session_expires = True
log_to_file = True
ffmpeg_path = 
run_at_start =
run_at_finish =
use_locks = True
clear_temp_files = False
skip_merge = False
    """
    LOGIN_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', "x-ig-app-id": '936619743392459'}
    LOGIN_URL = 'https://www.instagram.com/accounts/login/'
    AJAX_LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    REELS_TRAY_URL = 'https://i.instagram.com/api/v1/live/reels_tray_broadcasts/'
    BROADCAST_HEALTH_URL = 'https://i.instagram.com/api/v1/live/{:s}/info/'
    BROADCAST_HEALTH2_URL = 'https://i.instagram.com/api/v1/live/{:s}/heartbeat_and_get_viewer_count/'
    BROADCAST_INFO_URL = 'https://www.instagram.com/{:s}/live/?__a=1'
    MAIN_SITE_URL = 'https://www.instagram.com/'