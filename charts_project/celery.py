from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE','charts_project.settings')

app = Celery('charts_project')
app.conf.enable_utc = False
app.conf.update(timezone = settings.TIME_ZONE)

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    'daily-data':{
        'task': 'home.tasks.dailyDataUpdate',
        'schedule': crontab(hour=20,minute=00),
    },
    'daily-line-data':{
        'task': 'home.tasks.dailyLineDataUpdate',
        'schedule': crontab(hour=19,minute=55),
    },
    'update-chart-every-month-second-friday':{
        'task': 'home.tasks.updateChart11to20Every2ndFriday',
        'schedule': crontab(hour=19,minute=50,day_of_week='friday',day_of_month='8-14'),
    },
    'update-chart-every-quater-second-friday':{
        'task': 'home.tasks.updateChart1to10EveryQuater2ndFriday',
        'schedule': crontab(hour=19,minute=45,day_of_week='friday',day_of_month='8-14',month_of_year='3,6,9,12'),
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
