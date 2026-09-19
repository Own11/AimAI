from django.urls import path
from .views import focus_analytics, focus_home, focus_start, focus_stop

urlpatterns = [
    path('', focus_home, name='focus-home'),
    path('analytics/', focus_analytics, name='focus-analytics'),
    path('start/', focus_start, name='focus-start'),
    path('<int:pk>/stop/', focus_stop, name='focus-stop'),
]
