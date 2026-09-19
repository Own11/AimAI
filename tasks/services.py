from datetime import timedelta
from django.utils import timezone
from .models import Task


def reschedule_overdue_tasks(owner=None):
    now = timezone.now()
    queryset = Task.objects.filter(status=Task.Status.TODO, due_at__lt=now, is_rest_day=False)
    if owner is not None:
        queryset = queryset.filter(owner=owner)
    updated = 0
    for task in queryset:
        task.due_at = now + timedelta(hours=24)
        task.save(update_fields=['due_at'])
        updated += 1
    return updated
