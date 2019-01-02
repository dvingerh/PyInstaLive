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
    global dl_path
    global dl_lives
    global dl_replays
    global dl_comments
    global log_to_file
    global run_at_start
    global run_at_finish
    global show_cookie_expiry
    global config_path
    global config
    global args
    global uargs
    global livestream_obj
    global replays_obj
    global broadcast_downloader
    global epochtime
    global datetime_compat
    global live_folder_path
    global use_locks
    global comment_thread_worker
    global segments_json_thread_worker
    global assemble_arg
    global ffmpeg_path
    global clear_temp_files
    global has_guest
    ig_api = None
    ig_user = ""
    ig_pass = ""
    dl_user = ""
    dl_path = os.getcwd()
    dl_lives = True
    dl_replays = True
    dl_comments = True
    log_to_file = True
    run_at_start = ""
    run_at_finish = ""
    show_cookie_expiry = False
    config_path = os.path.join(os.getcwd(), "pyinstalive.ini")
    config = None
    args = None
    uargs = None
    livestream_obj = None
    replays_obj = None
    broadcast_downloader = None
    epochtime = helpers.strepochtime()
    datetime_compat = helpers.strdatetime_compat(epochtime)
    live_folder_path = ""
    use_locks = True
    comment_thread_worker = None
    segments_json_thread_worker = None
    assemble_arg = None
    ffmpeg_path = None
    clear_temp_files = False
    has_guest = None
