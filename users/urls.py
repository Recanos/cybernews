from django.urls import path
from django.contrib.auth import views as auth_views
from allauth.account.views import PasswordResetView
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('login/', auth_views.LoginView.as_view(
        template_name='allauth/account/login.html'
    ), name='login'),
    path('password/reset/', PasswordResetView.as_view(
        template_name='account/password_reset.html'
    ), name='account_reset_password'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
] 