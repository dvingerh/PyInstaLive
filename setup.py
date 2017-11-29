from setuptools import setup

__author__ = 'notcammy'
__email__ = 'neus2benen@gmail.com'
__version__ = '2.2.9'

_api_version = '1.3.5'
_api_extensions_version = '0.3.6'

long_description = 'This script enables you to record Instagram livestreams as well as download any available replays. It is based on another script that has now been discontinued.'

setup(
	name='pyinstalive',
	version=__version__,
	author=__author__,
	author_email=__email__,
	url='https://github.com/notcammy/PyInstaLive',
	packages=['pyinstalive'],
	entry_points={
		'console_scripts': [
			'pyinstalive = pyinstalive.__main__:run',
		]
	},
	install_requires=[ 
		'instagram_private_api>=%(api)s' % {'api': _api_version},
		'instagram_private_api_extensions>=%(ext)s' % {'ext': _api_extensions_version},
		'argparse',
		'configparser'
	],
	dependency_links=[
		'https://github.com/ping/instagram_private_api/archive/%(api)s.tar.gz'
		'#egg=instagram_private_api-%(api)s' % {'api': _api_version},
		'https://github.com/ping/instagram_private_api_extensions/archive/%(ext)s.tar.gz'
		'#egg=instagram_private_api_extensions-%(ext)s' % {'ext': _api_extensions_version}
	],
	include_package_data=True,
	platforms='any',
	long_description=long_description,
	keywords='instagram-livestream-recorder record-instagram-livestreams live instagram record livestream video recorder downloader download save',
	description='This script enables you to record Instagram livestreams.',
	classifiers=[
		'Environment :: Console',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
	]
)
