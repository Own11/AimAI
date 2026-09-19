from celery import shared_task
from .services import reschedule_overdue_tasks


@shared_task
def reschedule_overdue_tasks_task():
    return reschedule_overdue_tasks()
