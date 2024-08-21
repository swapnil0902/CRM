from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import customer
from django.conf.urls import handler403

urlpatterns = [
    path('', customer, name='customer-view'),
]
