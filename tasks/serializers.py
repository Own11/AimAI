from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_at', 'status', 'streak', 'best_streak', 'missed_count', 'is_rest_day', 'created_at', 'completed_at']
        read_only_fields = ['id', 'status', 'streak', 'best_streak', 'missed_count', 'created_at', 'completed_at']
