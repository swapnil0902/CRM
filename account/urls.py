from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from crm_home import views as crm_homeview
from customer import views as cust_views
from lead import views as ld_views
from appointment import views as appt_views

urlpatterns = [
    ################### Login, Logout, signup, contact-admin #####################################
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/<int:request_id>/', views.signup, name='signup'),
    path('signup/', views.manual_signup, name='Msignup'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.user_request_view, name='customer_request'),
    
    ########################## request ###########################################################
    path('user-requests/', views.user_requests_view, name='user_requests'),
    path('request-submitted/', views.request_submitted_view, name='request_submitted'),
    path('create-company-from-request/<int:request_id>/', crm_homeview.prefilled_create_company, name='prefilled_create_company'),
    path('list-new-company-requests/', views.list_new_company_requests, name='list_new_company_requests'),

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
    path('company_appointment/<int:appointment_id>/', appt_views.company_appointment_update, name='company_appointment_update'),
    path('company_appointment/<int:appointment_id>/delete/', appt_views.company_appointment_delete, name='company_appointment_delete'),
    
    
    
    
    
  



    # path('company-request-submitted/', views.TemplateView.as_view(template_name='account/company_request_submitted.html'), name='company_request_submitted'),

]
