from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.complete()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        task = self.get_object()
        text = str(request.data.get('text', '')).strip()
        if not text:
            return Response({'detail': 'text is required'}, status=400)
        tags = request.data.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        from .models import FailureLog
        FailureLog.objects.create(task=task, text=text, tags=tags)
        task.register_failure()
        return Response(self.get_serializer(task).data)
