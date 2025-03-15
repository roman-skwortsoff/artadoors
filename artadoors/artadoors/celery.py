from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указываем, какой settings-файл использовать для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artadoors.settings.dev')

app = Celery('artadoors')

# Подключаем настройки из Django, используя пространство имен CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находит задачи во всех установленных приложениях
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
