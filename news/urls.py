from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('search/', views.news_search, name='news_search'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('category/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('category/<slug:category_slug>/', views.news_list, name='news_list_by_category'),
    path('tag/create/', views.create_tag, name='create_tag'),
    path('tag/<int:pk>/edit/', views.edit_tag, name='edit_tag'),
    path('tag/<int:pk>/delete/', views.delete_tag, name='delete_tag'),
    path('tag/<slug:tag_slug>/', views.news_list, name='news_list_by_tag'),
    path('news/create/', views.create_news, name='create_news'),
    path('news/<slug:slug>/edit/', views.edit_news, name='edit_news'),
    path('news/<slug:slug>/delete/', views.delete_news, name='delete_news'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('news/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/dislike/', views.dislike_comment, name='dislike_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
] 