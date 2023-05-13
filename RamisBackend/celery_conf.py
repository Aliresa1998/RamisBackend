from __future__ import absolute_import
from celery import Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RamisBackend.settings')

celery_app = Celery('RamisBackend')
celery_app.config_from_object('django.conf.settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
