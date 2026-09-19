from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Task, FailureLog
from services.ai import analyze_task
from django.utils import timezone
from .parser import parse_task_text


@login_required
def task_list(request):
    from focus.models import FocusSession
    tasks = Task.objects.filter(owner=request.user)
    sessions = FocusSession.objects.filter(user=request.user, ended_at__isnull=False)
    completed = tasks.filter(status=Task.Status.DONE).count()
    focus_minutes = sum(session.duration_minutes for session in sessions)
    active = tasks.filter(status=Task.Status.TODO).order_by('due_at')
    return render(request, 'tasks/list.html', {
        'tasks': tasks, 'active_tasks': active[:5], 'completed_count': completed,
        'focus_minutes': focus_minutes, 'streak': max((task.streak for task in tasks), default=0),
    })


@login_required
def day_plan(request):
    energy = request.GET.get('energy', 'medium')
    tasks = Task.objects.filter(owner=request.user, status=Task.Status.TODO, is_rest_day=False, due_at__date=timezone.localdate())
    if energy == 'low':
        tasks = tasks.order_by('due_at')[:3]
    elif energy == 'high':
        tasks = tasks.order_by('-due_at')
    else:
        tasks = tasks.order_by('due_at')
    return render(request, 'tasks/plan.html', {'tasks': tasks, 'energy': energy})


@login_required
@require_POST
def task_parse(request):
    for item in parse_task_text(request.POST.get('text', '')):
        Task.objects.create(owner=request.user, title=item['title'], due_at=item['due_at'])
    return redirect('task-list')


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    return render(request, 'tasks/detail.html', {'task': task})


@login_required
@require_POST
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    title = request.POST.get('title', '').strip()
    due_at = request.POST.get('due_at', '').strip()
    if not title or not due_at:
        return redirect('task-detail', pk=task.pk)
    task.title = title
    task.description = request.POST.get('description', '')
    task.due_at = due_at
    task.save(update_fields=['title', 'description', 'due_at'])
    return redirect('task-detail', pk=task.pk)


@login_required
@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.delete()
    return redirect('task-list')


@login_required
@require_POST
def task_rest_day(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.is_rest_day = True
    task.save(update_fields=['is_rest_day'])
    return redirect('task-list')


@login_required
@require_POST
def task_create(request):
    title = request.POST.get('title', '').strip()
    due_at = request.POST.get('due_at', '').strip()
    if title and due_at:
        Task.objects.create(owner=request.user, title=title, due_at=due_at)
    return redirect('task-list')


@login_required
@require_POST
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.complete()
    return redirect('task-list')


@login_required
def failure_modal(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    return render(request, 'tasks/failure_modal.html', {'task': task})


@login_required
@require_POST
def failure_create(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    tags = [tag.strip() for tag in request.POST.get('tags', '').split(',') if tag.strip()]
    FailureLog.objects.create(task=task, tags=tags, text=request.POST['text'])
    task.register_failure()
    return redirect('task-list')


@login_required
@require_POST
def task_analyze(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    analyze_task(task)
    return redirect('insight-list')

# Create your views here.
