from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    path('', views.tournament_list, name='tournament_list'),
    path('schedule/', views.match_schedule, name='match_schedule'),
    path('results/', views.match_results, name='match_results'),
    path('team/<int:pk>/', views.team_detail, name='team_detail'),
    path('match/<int:pk>/', views.match_detail, name='match_detail'),
    path('<int:pk>/', views.tournament_detail, name='tournament_detail'),
] 