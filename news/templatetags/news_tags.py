from django import template
from news.models import Comment, News

register = template.Library()

@register.filter(name='has_liked')
def has_liked(obj, user):
    if not user.is_authenticated:
        return False
    if isinstance(obj, Comment):
        return obj.has_user_liked(user)
    elif isinstance(obj, News):
        return obj.has_user_liked(user)
    return False

@register.filter(name='has_disliked')
def has_disliked(obj, user):
    if not user.is_authenticated:
        return False
    if isinstance(obj, Comment):
        return obj.has_user_disliked(user)
    elif isinstance(obj, News):
        return obj.has_user_disliked(user)
    return False

@register.filter(name='get_popularity')
def get_popularity(comment):
    """Возвращает разницу между количеством лайков и дизлайков для сортировки по популярности"""
    return comment.get_likes_count() - comment.get_dislikes_count() 