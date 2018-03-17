import os
import sys

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
        return False
    return True

def log(string, color):
	if not supports_color():
		print(string)
	else:
		print('\033[1m' + colors(color) + string + colors("ENDC"))

def seperator(color):
	if not supports_color():
		print("-" * 70)
	else:
		print('\033[1m' + colors(color) + ("-" * 70) + colors("ENDC"))
