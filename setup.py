from setuptools import setup

__author__ = 'dvingerh'
__email__ = 'dirk.ving@gmail.com'
__version__ = '4.0.1'


long_description = 'This Python script enables you to download ongoing Instagram livestreams as a video file.'

setup(
    name='pyinstalive',
    version=__version__,
    author=__author__,
    author_email=__email__,
    url='https://github.com/dvingerh/PyInstaLive',
    packages=['pyinstalive'],
    entry_points={
        'console_scripts': [
            'pyinstalive = pyinstalive.__main__:run',
        ]
    },
    install_requires=[
        'argparse',
        'configparser'
    ],
    include_package_data=True,
    platforms='any',
    long_description=long_description,
    keywords='instagram-livestream-recorder record-instagram-livestreams live instagram record livestream video '
             'recorder downloader download save',
    description='Download Instagram livestreams.',
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
