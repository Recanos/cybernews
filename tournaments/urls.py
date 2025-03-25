from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    path('', views.tournament_list, name='tournament_list'),
    path('<slug:slug>/', views.tournament_detail, name='tournament_detail'),
    path('team/<slug:slug>/', views.team_detail, name='team_detail'),
    path('match/<int:pk>/', views.match_detail, name='match_detail'),
    path('schedule/', views.match_schedule, name='match_schedule'),
    path('results/', views.match_results, name='match_results'),
] 