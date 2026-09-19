from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import FocusSession
from tasks.models import Task


@login_required
def focus_home(request):
    active = FocusSession.objects.filter(user=request.user, ended_at__isnull=True).first()
    sessions = FocusSession.objects.filter(user=request.user, ended_at__isnull=False).order_by('-started_at')[:10]
    total_minutes = sum(session.duration_minutes for session in sessions)
    return render(request, 'focus/home.html', {'active': active, 'tasks': Task.objects.filter(owner=request.user, status=Task.Status.TODO), 'sessions': sessions, 'total_minutes': total_minutes})


@login_required
def focus_analytics(request):
    sessions = FocusSession.objects.filter(user=request.user, ended_at__isnull=False)
    total = sum(item.duration_minutes for item in sessions)
    by_task = {}
    for item in sessions:
        by_task[item.task.title] = by_task.get(item.task.title, 0) + item.duration_minutes
    return render(request, 'focus/analytics.html', {'total': total, 'by_task': by_task})


@login_required
@require_POST
def focus_start(request):
    FocusSession.objects.filter(user=request.user, ended_at__isnull=True).update(ended_at=timezone.now())
    task = get_object_or_404(Task, pk=request.POST['task_id'], owner=request.user)
    try:
        duration = int(request.POST.get('duration', 25))
    except (TypeError, ValueError):
        duration = 25
    duration = duration if duration in (25, 50) else 25
    FocusSession.objects.create(user=request.user, task=task, started_at=timezone.now(), duration_minutes=duration)
    return redirect('focus-home')


@login_required
@require_POST
def focus_stop(request, pk):
    session = get_object_or_404(FocusSession, pk=pk, user=request.user, ended_at__isnull=True)
    session.ended_at = timezone.now()
    elapsed = max(1, round((session.ended_at - session.started_at).total_seconds() / 60))
    session.duration_minutes = min(elapsed, session.duration_minutes)
    session.save(update_fields=['ended_at', 'duration_minutes'])
    return redirect('focus-home')

# Create your views here.
