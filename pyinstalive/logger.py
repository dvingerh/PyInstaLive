import os
import sys
from .settings import settings

sep = "-" * 70

def colors(state):
	color = ''

	if (state == 'BLUE'):
		color = '\033[94m'

	if (state == 'GREEN'):
		color = '\033[92m'

	if (state == 'YELLOW'):
		color = '\033[93m'

	if (state == 'RED'):
		color = '\033[91m'

	if (state == 'ENDC'):
		color = '\033[0m'

	if (state == 'WHITE'):
		color = '\033[0m'

	return color

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

def log(string, color):
	if supports_color()[1] == False:
		print(string)
	else:
		print('\033[1m{}{}{}'.format(colors(color), string, colors("ENDC")))
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive_{:s}.log".format(settings.user_to_download),"a+") as f:
				f.write("{:s}\n".format(string))
				f.close()
		except:
			pass
	sys.stdout.flush()

def seperator(color):
	if supports_color()[1] == False:
		print(sep)
	else:
		print('\033[1m{}{}{}'.format(colors(color), sep, colors("ENDC")))
	if settings.log_to_file == 'True':
		try:
			with open("pyinstalive_{:s}.log".format(settings.user_to_download),"a+") as f:
				f.write("{:s}\n".format(sep))
				f.close()
		except:
			pass
	sys.stdout.flush()