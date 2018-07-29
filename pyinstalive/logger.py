import os
import sys
import re
from .settings import settings

sep = "-" * 70

def supports_color():
	"""
	from https://github.com/django/django/blob/master/django/core/management/color.py
	Return True if the running system's terminal supports color,
	and False otherwise.
	"""

	plat = sys.platform
	supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)

	# isatty is not always implemented, #6223.
	is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
	if not supported_platform or not is_a_tty:
		return "No", False
	return "Yes", True


def log_seperator():
	print(sep + "\033[0m")
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive{:s}.log".format("_" + settings.user_to_download if len(settings.user_to_download) > 0 else ".default"),"a+") as f:
				f.write(sep + '\n')
				f.close()
		except:
			pass
	sys.stdout.flush()





def log_info_green(string):
	if supports_color()[1] == False:
		print(string)
	else:
		print('[\033[92mI\033[0m] {:s}\033[0m'.format(string))
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive{:s}.log".format("_" + settings.user_to_download if len(settings.user_to_download) > 0 else ".default"),"a+") as f:
				f.write("[I] {:s}\n".format(string))
				f.close()
		except:
			pass
	sys.stdout.flush()

def log_info_blue(string):
	if supports_color()[1] == False:
		print(string)
	else:
		print('[\033[94mI\033[0m] {:s}\033[0m'.format(string))
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive{:s}.log".format("_" + settings.user_to_download if len(settings.user_to_download) > 0 else ".default"),"a+") as f:
				f.write("[I] {:s}\n".format(string))
				f.close()
		except:
			pass
	sys.stdout.flush()

def log_warn(string):
	if supports_color()[1] == False:
		print(string)
	else:
		print('[\033[93mW\033[0m] {:s}\033[0m'.format(string))
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive{:s}.log".format("_" + settings.user_to_download if len(settings.user_to_download) > 0 else ".default"),"a+") as f:
				f.write("[W] {:s}\n".format(string))
				f.close()
		except:
			pass
	sys.stdout.flush()

def log_error(string):
	if supports_color()[1] == False:
		print(string)
	else:
		print('[\033[91mE\033[0m] {:s}\033[0m'.format(string))
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive{:s}.log".format("_" + settings.user_to_download if len(settings.user_to_download) > 0 else ".default"),"a+") as f:
				f.write("[E] {:s}\n".format(string))
				f.close()
		except:
			pass
	sys.stdout.flush()

def log_whiteline():
	print("")
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive{:s}.log".format("_" + settings.user_to_download if len(settings.user_to_download) > 0 else ".default"),"a+") as f:
				f.write("\n")
				f.close()
		except:
			pass
	sys.stdout.flush()

def log_plain(string):
	print(string)
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive{:s}.log".format("_" + settings.user_to_download if len(settings.user_to_download) > 0 else ".default"),"a+") as f:
				f.write("{:s}\n".format(string))
				f.close()
		except:
			pass
	sys.stdout.flush()