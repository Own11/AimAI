from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'todo', 'К выполнению'
        DONE = 'done', 'Выполнена'
        PAUSED = 'paused', 'На паузе'

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TODO)
    streak = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    missed_count = models.PositiveIntegerField(default=0)
    is_rest_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('status', 'due_at')

    def __str__(self):
        return self.title

    def complete(self):
        self.status = self.Status.DONE
        self.completed_at = timezone.now()
        self.streak += 1
        self.best_streak = max(self.best_streak, self.streak)
        self.save(update_fields=['status', 'completed_at', 'streak', 'best_streak'])

    def register_failure(self):
        self.missed_count += 1
        self.streak = 0
        if self.missed_count >= 2:
            self.status = self.Status.PAUSED
        self.save(update_fields=['missed_count', 'streak', 'status'])


class FailureLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='failures')
    tags = models.JSONField(default=list)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


class Intervention(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='interventions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
