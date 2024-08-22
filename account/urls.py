from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from crm_home import views as crm_homeview
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/<int:request_id>/', views.signup, name='signup'),
    path('signup/', views.manual_signup, name='Msignup'),
    path('contact/', views.customer_request_view, name='customer_request'),
    path('mngr-dashboard/', views.mngr_dashboard, name='mngr_dashboard'),
    path('customer-requests/', views.customer_requests_view, name='customer_requests'),
    path('request-submitted/', views.request_submitted_view, name='request_submitted'),
    path('groups/', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('create-group/', views.group_create, name='group_create'),
    path('update-group/<int:pk>/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('activate/', views.activate_password, name='activate_password'),
    path('logout', views.logout_view, name='logout'),
    path('request-company/', views.company_request_view, name='request_company'),
    path('create-company/', crm_homeview.create_company, name="create_company"),
    path('companies/', crm_homeview.company_list, name='company_list'),
    path('company/<int:pk>/', crm_homeview.company_detail, name='company_detail'),
    path('list-new-company-requests/', views.list_new_company_requests, name='list_new_company_requests'),
    path('create-company-from-request/<int:request_id>/', crm_homeview.prefilled_create_company, name='prefilled_create_company'),



    # path('company-request-submitted/', views.TemplateView.as_view(template_name='account/company_request_submitted.html'), name='company_request_submitted'),

]
