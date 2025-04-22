from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('favorites/', views.favorites, name='favorites'),
    path('history/', views.view_history, name='view_history'),
    path('login/', auth_views.LoginView.as_view(
        template_name='allauth/account/login.html',
        authentication_form=CustomLoginForm
    ), name='login'),
] 