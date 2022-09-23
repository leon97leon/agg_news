from __future__ import absolute_import
import os
from celery import Celery

from my_site.settings import INSTALLED_APPS

# this code copied from manage.py
# set the default Django settings module for the 'celery' app.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_site.settings')

# you change the name here
app = Celery("my_site")

# read config from Django settings, the CELERY namespace would make celery
# config keys has `CELERY` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# load tasks.py in django apps
app.autodiscover_tasks(lambda: INSTALLED_APPS)
# app.control.add_consumer('foo', reply=True)
# app.control.add_consumer('foo1', reply=True)
# app.control.add_consumer('foo2', reply=True)
# app.control.add_consumer('queue2', reply=True)
# app.control.add_consumer('queue3', reply=True)