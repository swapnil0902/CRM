from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from crm_home import views as crm_homeview
urlpatterns = [
    path('test1/', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/<int:request_id>/', views.signup, name='signup'),
    path('signup/', views.manual_signup, name='Msignup'),
    path('contact/', views.customer_request_view, name='customer_request'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('customer-requests/', views.customer_requests_view, name='customer_requests'),
    path('request-submitted/', views.request_submitted_view, name='request_submitted'),
    path('groups/', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('create-group/', views.group_create, name='group_create'),
    path('update-group/<int:pk>/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('activate/', views.activate_password, name='activate_password'),
    path('create-company/', crm_homeview.create_company, name='create_company'),
    path('companies/', crm_homeview.company_list, name='company_list'),
    path('company/<int:pk>/', crm_homeview.company_detail, name='company_detail'),
]
