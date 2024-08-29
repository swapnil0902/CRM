from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from crm_home import views as crm_homeview
from customer import views as cust_views
from lead import views as ld_views
from appointment import views as appt_views
from task import views as tk_views

urlpatterns = [
    ################### Login, Logout, signup, contact-admin #####################################
    path('login/', views.CustomLoginView.as_view(template_name='account/login.html'), name='login'),
    path('signup/<int:request_id>/', views.signup, name='signup'),
    path('signup/', views.manual_signup, name='Msignup'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.user_request_view, name='user_request'),
    
    ########################## request ###########################################################
    path('user-requests/', views.user_requests_view, name='user_requests'),
    path('request-submitted/', views.request_submitted_view, name='request_submitted'),
    path('create-company-from-request/<int:request_id>/', crm_homeview.prefilled_create_company, name='prefilled_create_company'),
    path('list-new-company-requests/', views.list_new_company_requests, name='list_new_company_requests'),

    ############################# groups #########################################################
    path('groups/', views.group_list, name='group_list'),
    path('create-group/', views.group_create, name='group_create'),
    path('update-group/<int:pk>/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    
    path('groups-Admin/', views.group_list_Admin, name='group_list_Admin'),
    path('create-group-Admin/', views.group_create_Admin, name='group_create_Admin'),
    path('update-group-Admin/<int:pk>/', views.group_update_Admin, name='group_update_Admin'),
    path('groups-Admin/<int:pk>/delete/', views.group_delete_Admin, name='group_delete_Admin'),

    ##################################### dashboards #############################################
    path('mngr-dashboard/', views.mngr_dashboard, name='mngr_dashboard'),
   
    #################################### companies #######################################
    path('companies/', crm_homeview.company_list, name='company_list'),
    path('company/<int:pk>/', crm_homeview.company_detail, name='company_detail'),
    path('create-company/', crm_homeview.create_company, name="create_company"),
    path('request-company/', views.company_request_view, name='request_company'),

    #################################### customer list ###########################################
    path('company_customers/', cust_views.company_customer_list, name='company_customer_list'),
    path('company_customers/<int:customer_id>/', cust_views.company_customer_detail, name='company_customer_detail'),
    path('company_customers/<int:customer_id>/delete/', cust_views.company_customer_delete, name='company_customer_delete'),

    #################################### lead list ###########################################
    path('company_lead/', ld_views.company_lead_list, name='company_lead_list'),
    path('company_lead/<int:lead_id>/', ld_views.company_lead_detail, name='company_lead_detail'),
    path('company_lead/<int:lead_id>/delete/', ld_views.company_lead_delete, name='company_lead_delete'),
    
    #################################### appointment list ###########################################
    path('company_appointment/', appt_views.company_appointment_list, name='company_appointment_list'),
    path('company_appointment/<int:pk>/', appt_views.company_appointment_update, name='company_appointment_update'),
    path('company_appointment/<int:pk>/delete/', appt_views.company_appointment_delete, name='company_appointment_delete'),
        
    #################################### task list ###########################################
    path('company_task/', tk_views.company_task_list, name='company_task_list'),
    path('company_task/<int:pk>/', tk_views.company_task_update, name='company_task_update'),
    path('company_task/<int:pk>/delete/', tk_views.company_task_delete, name='company_task_delete'),

    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'), 

    #################################### delete account ###########################################
    path('delete_account/', views.delete_account, name='delete_account'),
    path('delete_user/<int:user_id>/', views.delete_my_user, name='delete_my_user'),
    
]
