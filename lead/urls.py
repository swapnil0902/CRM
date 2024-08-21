from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import lead, lead_detail, lead_create
from django.conf.urls import handler403

urlpatterns = [
    path('', lead, name='lead-view'),
    path('create/', lead_create, name='lead_create'),
    path('<int:lead_id>/', lead_detail, name='lead_detail'),
]
