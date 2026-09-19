import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('aimai')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'reschedule-overdue-every-hour': {
        'task': 'tasks.tasks.reschedule_overdue_tasks_task',
        'schedule': 3600.0,
    },
}
