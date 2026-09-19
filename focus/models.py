from django.db import models
from django.contrib.auth.models import User
from tasks.models import Task


class FocusSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='focus_sessions')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=25)

# Create your models here.
