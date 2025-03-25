from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('favorites/', views.favorites, name='favorites'),
    path('history/', views.view_history, name='view_history'),
] 