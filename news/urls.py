from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('category/<slug:category_slug>/', views.news_list, name='news_list_by_category'),
    path('tag/<slug:tag_slug>/', views.news_list, name='news_list_by_tag'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('news/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('search/', views.news_search, name='news_search'),
] 