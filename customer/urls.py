from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import customer_list, customer_create, customer_delete, customer_detail
from django.conf.urls import handler403

urlpatterns = [
    path('', customer_list, name='customer-view'),
    path('create/', customer_create, name='customer_create'),
    path('<int:customer_id>/', customer_detail, name='customer_detail'),
    path('<int:customer_id>/delete/', customer_delete, name='customer_delete'),
]
