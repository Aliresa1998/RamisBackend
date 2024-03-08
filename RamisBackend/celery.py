# RamisBackend/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RamisBackend.settings')

app = Celery('RamisBackend')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in applications' tasks.py
app.autodiscover_tasks()

# Schedule
app.conf.beat_schedule = {
    'get_user_total_balance_every_midnight': {
        'task': 'your_app_name.tasks.get_user_total_balance',
        'schedule': crontab(hour=0, minute=0),
        # Optionally, you can add arguments to 'args': (arg1, arg2...)
    },
}
