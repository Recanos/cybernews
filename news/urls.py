from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('search/', views.news_search, name='news_search'),
    path('category/<slug:category_slug>/', views.news_list, name='news_list_by_category'),
    path('tag/<slug:tag_slug>/', views.news_list, name='news_list_by_tag'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('news/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/dislike/', views.dislike_comment, name='dislike_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('news/<slug:slug>/like/', views.like_news, name='like_news'),
    path('news/<slug:slug>/dislike/', views.dislike_news, name='dislike_news'),
] 