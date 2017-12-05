#!/usr/bin/env python3
"""
For WSGI Server
To run:
$ gunicorn -b 0.0.0.0:5000 wsgi:app
OR
$ export FLASK_APP=wsgi
$ flask run
"""
import os
from appname import create_app

env = os.environ.get('APPNAME_ENV', 'dev')
app = create_app('appname.settings.%sConfig' % env.capitalize())
