from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Insight


@login_required
def insight_list(request):
    insights = Insight.objects.filter(user=request.user)
    return render(request, 'insights/list.html', {'insights': insights})
