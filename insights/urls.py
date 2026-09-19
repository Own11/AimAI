from django.urls import path
from .views import insight_list

urlpatterns = [path('', insight_list, name='insight-list')]
