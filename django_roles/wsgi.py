"""
WSGI config for django_roles project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import sys
path = os.path.expanduser('~/etiac') #Este es el nombre de la carpeta general, ejemplo:
#si la carpeta se llama pythonanywhere se debe llamar pythonanywhere
if path not in sys.path:
    sys.path.insert(0,path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_roles.settings' #django_roles es el nombre 
#de la carpeta donde esta el settings
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler
application = StaticFilesHandler(get_wsgi_application())