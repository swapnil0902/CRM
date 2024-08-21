from django.urls import path, include
from rest_framework.routers import DefaultRouter
from task import views
from django.conf.urls import handler403

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('createtask/', views.task_create, name='task_create'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/update/', views.update_task, name='task_update'),
    path('task/<int:pk>/delete/', views.delete_task, name='task_delete'),
]
