import os
import sys	
sys.path.append('/home/usernews/my_site')
os.environ['DJANGO_SETTINGS_MODULE'] = 'my_site.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()