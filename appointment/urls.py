# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),  
    path('create/', views.appointment_create, name='appointment_create'), 
    path('<int:pk>/update/', views.appointment_update, name='appointment_update'),  
    path('<int:pk>/delete/', views.appointment_delete, name='appointment_delete'), 
]
