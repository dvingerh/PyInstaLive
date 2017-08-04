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

def log(string, color):
	print('\033[1m' + colors(color) + string + colors("ENDC"))

def seperator(color):
	print('\033[1m' + colors(color) + ("-" * 50) + colors("ENDC"))