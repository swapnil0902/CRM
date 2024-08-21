from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  lead_list, lead_detail, lead_create, lead_delete
from django.conf.urls import handler403

urlpatterns = [
    path('', lead_list, name='lead-view'),
    path('create/', lead_create, name='lead_create'),
    path('<int:lead_id>/', lead_detail, name='lead_detail'),
    path('<int:lead_id>/delete/', lead_delete, name='lead_delete'),
]
