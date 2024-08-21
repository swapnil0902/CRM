from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('test1/', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('groups/', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/update/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('activate/', views.activate_password, name='activate_password'),
]
