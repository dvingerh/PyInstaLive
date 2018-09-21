import time

class settings:
	user_to_download = ""
	username = ""
	password = ""
	save_path = "/"
	ffmpeg_path = None
	show_cookie_expiry = "true"
	clear_temp_files = "false"
	current_time = str(int(time.time()))
	current_date = time.strftime("%Y%m%d")
	save_replays = "true"
	save_lives = "true"
	run_at_start = "None"
	run_at_finish = "None"
	save_comments = "true"
	log_to_file = "false"