from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Intervention


@login_required
def intervention_list(request):
    interventions = Intervention.objects.filter(task__owner=request.user).select_related('task')
    return render(request, 'interventions/list.html', {'interventions': interventions})


@login_required
@require_POST
def intervention_apply(request, pk):
    intervention = get_object_or_404(Intervention, pk=pk, task__owner=request.user)
    intervention.is_applied = True
    intervention.save(update_fields=['is_applied'])
    return redirect('intervention-list')
