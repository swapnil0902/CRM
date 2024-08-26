from django.urls import path
from .views import  lead_list, lead_detail, lead_create, lead_delete

urlpatterns = [
    path('', lead_list, name='lead-view'),
    path('create/', lead_create, name='lead_create'),
    path('<int:lead_id>/', lead_detail, name='lead_detail'),
    path('<int:lead_id>/delete/', lead_delete, name='lead_delete'),
]
