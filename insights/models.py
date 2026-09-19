from django.db import models
from django.contrib.auth.models import User


class Insight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insights')
    title = models.CharField(max_length=255)
    body = models.TextField()
    confidence = models.DecimalField(max_digits=4, decimal_places=3, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
