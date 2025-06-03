from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    # Tournament URLs
    path('', views.tournament_list, name='tournament_list'),
    path('create/', views.create_tournament, name='create_tournament'),
    path('<int:pk>/', views.tournament_detail, name='tournament_detail'),
    path('<int:pk>/edit/', views.edit_tournament, name='edit_tournament'),
    path('<int:pk>/delete/', views.delete_tournament, name='delete_tournament'),
    
    # Team URLs
    path('team/<int:pk>/', views.team_detail, name='team_detail'),
    path('team/create/', views.create_team, name='create_team'),
    path('team/<int:pk>/edit/', views.edit_team, name='edit_team'),
    path('team/<int:pk>/delete/', views.delete_team, name='delete_team'),
    
    # Match URLs
    path('match/create/', views.create_match, name='create_match'),
    path('match/<int:pk>/edit/', views.edit_match, name='edit_match'),
    path('match/<int:pk>/delete/', views.delete_match, name='delete_match'),

    path('tournament/<int:tournament_pk>/team/<int:team_pk>/add/', views.add_team_to_tournament, name='add_team_to_tournament'),
    path('tournament/<int:tournament_pk>/team/<int:team_pk>/remove/', views.remove_team_from_tournament, name='remove_team_from_tournament'),
] 