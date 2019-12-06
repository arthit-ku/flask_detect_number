#! /usr/bin/python3

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/flask_detect_number/')
from flask_app import app as application
application.secret_key = 'test123'
