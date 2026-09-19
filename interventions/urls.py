from django.urls import path
from .views import intervention_apply, intervention_list

urlpatterns = [
    path('', intervention_list, name='intervention-list'),
    path('<int:pk>/apply/', intervention_apply, name='intervention-apply'),
]
