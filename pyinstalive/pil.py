try:
    import logger
    import helpers
except ImportError:
    from . import logger
    from . import helpers
import os


def noinit(self):
    pass


def initialize():
    global ig_api
    global ig_user
    global ig_pass
    global dl_user
    global dl_batchusers
    global dl_path
    global dl_comments
    global log_to_file
    global cmd_on_started
    global cmd_on_ended
    global show_session_expires
    global config_path
    global config
    global args
    global uargs
    global initial_livestream_obj
    global livestream_downloader
    global epochtime
    global datetime_compat
    global live_folder_path
    global use_locks
    global assemble_arg
    global ffmpeg_path
    global clear_temp_files
    global has_guest
    global skip_assemble
    global config_login_overridden
    global winbuild_path
    global livestream_downloaded_obj
    global heartbeat_info_thread_worker
    global json_thread_worker
    global comments_thread_worker
    global kill_threads
    global comments
    global comments_last_ts
    ig_api = None
    ig_user = ""
    ig_pass = ""
    dl_user = ""
    dl_batchusers = []
    dl_path = os.getcwd() + "/"
    dl_comments = False
    log_to_file = True
    cmd_on_started = ""
    cmd_on_ended = ""
    show_session_expires = False
    config_path = os.path.join(os.getcwd(), "pyinstalive.ini")
    config = None
    args = None
    uargs = None
    initial_livestream_obj = None
    livestream_downloader = None
    epochtime = helpers.strepochtime()
    datetime_compat = helpers.strdatetime_compat()
    live_folder_path = ""
    use_locks = True
    assemble_arg = None
    ffmpeg_path = None
    clear_temp_files = False
    has_guest = None
    skip_assemble = False
    config_login_overridden = False
    winbuild_path = helpers.winbuild_path()
    livestream_downloaded_obj = None
    heartbeat_info_thread_worker = None
    json_thread_worker = None
    comments_thread_worker = None
    kill_threads = False
    comments = []
    comments_last_ts = 0