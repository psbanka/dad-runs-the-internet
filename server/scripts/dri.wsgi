#!/usr/bin/env python

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tnt_web.web.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
