from task import views
from django.urls import path, include

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('createtask/', views.task_create, name='task_create'),
    path('<int:pk>/update/', views.update_task, name='task_update'),
    path('<int:pk>/delete/', views.delete_task, name='task_delete'),
]
