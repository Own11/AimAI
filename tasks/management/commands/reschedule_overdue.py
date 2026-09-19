from django.core.management.base import BaseCommand
from tasks.services import reschedule_overdue_tasks


class Command(BaseCommand):
    help = 'Переносит активные просроченные задачи на следующие сутки.'

    def handle(self, *args, **options):
        self.stdout.write(f'Rescheduled: {reschedule_overdue_tasks()}')
