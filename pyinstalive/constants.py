import sys


class Constants:
    SCRIPT_VER = "3.2.4"
    PYTHON_VER = sys.version.split(' ')[0]
    CONFIG_TEMPLATE = """
[pyinstalive]
username = johndoe
password = grapefruits
download_path = {:s}
download_lives = True
download_replays = True
download_comments = true
show_cookie_expiry = True
log_to_file = True
ffmpeg_path = 
run_at_start =
run_at_finish =
use_locks = True
clear_temp_files = False
do_heartbeat = True
proxy =
skip_merge = False
    """