import time

class settings:
	username = ""
	password = ""
	save_path = "/"
	show_cookie_expiry = "true"
	clear_temp_files = "false"
	current_time = str(int(time.time()))
	current_date = time.strftime("%Y%m%d")
	save_replays = "true"
	run_at_start = "None"
	run_at_finish = "None"
	save_comments = "true"
	ftp_host = "ftp.cluster020.hosting.ovh.net"
	ftp_save_path = "/"
	ftp_username = "milliemelp"
	ftp_password = "xXkzcdV9SMZU"
	ftp_enabled = False