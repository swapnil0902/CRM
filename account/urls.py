from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from crm_home import views as crm_homeview
from customer import views as cust_views
from lead import views as ld_views

urlpatterns = [
    ################### Login, Logout, signup, contact-admin #####################################
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/<int:request_id>/', views.signup, name='signup'),
    path('signup/', views.manual_signup, name='Msignup'),
    path('logout', views.logout_view, name='logout'),
    path('contact/', views.customer_request_view, name='customer_request'),
    
    ########################## request ###########################################################
    path('customer-requests/', views.customer_requests_view, name='customer_requests'),
    path('request-submitted/', views.request_submitted_view, name='request_submitted'),


    ############################# groups #########################################################
    path('groups/', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('create-group/', views.group_create, name='group_create'),
    path('update-group/<int:pk>/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),

    ##################################### dashboards #############################################
    path('mngr-dashboard/', views.mngr_dashboard, name='mngr_dashboard'),
   
    #################################### activate password #######################################
    path('activate/', views.activate_password, name='activate_password'),

    #################################### customer list ###########################################
    path('company_customers/', cust_views.company_customer_list, name='company_customer_list'),

    #################################### lead list ###########################################
    path('company_lead/', ld_views.company_lead_list, name='company_lead_list'),
]
