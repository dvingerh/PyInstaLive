import codecs
import datetime
import os.path
import logging
import argparse
import codecs
import sys, os, time, json

import cAuthCookie, cLogger, cDownloader

from socket import timeout, error as SocketError
from ssl import SSLError
from urllib2 import URLError
from httplib import HTTPException
from instagram_private_api_extensions import live

# "naxunaw" "pyinstalive" "credentials.json"

global api, args, seperator
parser = argparse.ArgumentParser(description='Login')
parser.add_argument('-u', '--username', dest='username', type=str, required=True)
parser.add_argument('-p', '--password', dest='password', type=str, required=True)
parser.add_argument('-r', '--record', dest='record', type=str, required=True)

args = parser.parse_args()

api = cAuthCookie.login(args.username, args.password)

cDownloader.main(api, args.record)