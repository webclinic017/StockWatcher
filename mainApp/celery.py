from __future__ import absolute_import
import logging
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for 'Celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockWatcher.settings')
app = Celery('celeryconfig')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# app.autodiscover_tasks()

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='EST5EDT',
    enable_utc=True,
)

@app.task(bind=True)
def debug_task(self):
  print('Request: {0!r}'.format(self.request))


if __name__ == '__main__':
  app.start()