"""
WSGI config for harta project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from . import scheduler
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harta.settings')

application = get_wsgi_application()



scheduler.start()