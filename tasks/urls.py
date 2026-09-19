from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task-list'),
    path('plan/', views.day_plan, name='day-plan'),
    path('parse/', views.task_parse, name='task-parse'),
    path('<int:pk>/', views.task_detail, name='task-detail'),
    path('<int:pk>/update/', views.task_update, name='task-update'),
    path('<int:pk>/delete/', views.task_delete, name='task-delete'),
    path('<int:pk>/rest-day/', views.task_rest_day, name='task-rest-day'),
    path('<int:pk>/analyze/', views.task_analyze, name='task-analyze'),
    path('create/', views.task_create, name='task-create'),
    path('<int:pk>/complete/', views.task_complete, name='task-complete'),
    path('<int:pk>/failure/', views.failure_modal, name='failure-modal'),
    path('<int:pk>/failure/create/', views.failure_create, name='failure-create'),
]
