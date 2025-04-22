from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import News, Category, Tag, Comment
from .forms import CommentForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token

def news_list(request, category_slug=None, tag_slug=None):
    news_list = News.objects.filter(is_published=True)
    category = None
    tag = None
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        news_list = news_list.filter(category=category)
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        news_list = news_list.filter(tags=tag)
    
    paginator = Paginator(news_list, 10)
    page = request.GET.get('page')
    news = paginator.get_page(page)
    
    return render(request, 'news/news_list.html', {
        'news': news,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'category': category,
        'tag': tag,
        'current_category': category,
        'current_tag': tag,
    })

def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    # Увеличиваем счетчик просмотров
    news.views_count += 1
    news.save()
    
    # Получаем похожие новости по тегам
    similar_news = News.objects.filter(
        is_published=True,
        tags__in=news.tags.all()
    ).exclude(id=news.id).distinct()[:5]
    
    # Получаем параметр сортировки комментариев
    sort_comments = request.GET.get('sort_comments', 'newest')
    
    # Получаем все комментарии к новости
    comments = news.comments.all()
    
    # Сортируем комментарии в зависимости от выбранного параметра
    if sort_comments == 'oldest':
        comments = comments.order_by('created_at')
    elif sort_comments == 'popular':
        # Сортируем по разнице между лайками и дизлайками
        comments = sorted(comments, key=lambda c: c.get_likes_count() - c.get_dislikes_count(), reverse=True)
    else:  # newest (по умолчанию)
        comments = comments.order_by('-created_at')
    
    # Форма для добавления комментария
    comment_form = CommentForm()
    
    # Получаем популярные теги (те, которые чаще всего используются)
    popular_tags = Tag.objects.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.news = news
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
            comment.save()
            messages.success(request, 'Комментарий успешно добавлен.')
            return redirect('news:news_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    # Добавляем CSRF токен в контекст для использования в AJAX запросах
    csrf_token = get_token(request)
    
    context = {
        'news': news,
        'similar_news': similar_news,
        'comments': comments,
        'comment_form': comment_form,
        'popular_tags': popular_tags,
        'sort_comments': sort_comments,
        'csrf_token': csrf_token,
    }
    return render(request, 'news/news_detail.html', context)

@login_required
def add_comment(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.news = news
            comment.author = request.user
            comment.is_approved = True  # Комментарии публикуются сразу
            
            # Обработка ответа на комментарий
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id, news=news)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
                
            comment.save()
            messages.success(request, 'Ваш комментарий успешно добавлен.')
            return redirect('news:news_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    return render(request, 'news/news_detail.html', {
        'news': news,
        'comment_form': comment_form,
    })

def news_search(request):
    query = request.GET.get('q')
    if query:
        news_list = News.objects.filter(
            is_published=True,
            title__icontains=query
        ) | News.objects.filter(
            is_published=True,
            content__icontains=query
        )
    else:
        news_list = News.objects.filter(is_published=True)
    
    paginator = Paginator(news_list, 10)
    page = request.GET.get('page')
    news = paginator.get_page(page)
    
    return render(request, 'news/news_list.html', {
        'news': news,
        'query': query,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    })

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Проверяем, что пользователь является автором комментария
    if comment.author != request.user:
        messages.error(request, 'У вас нет прав на удаление этого комментария.')
        return redirect('news:news_detail', slug=comment.news.slug)
    
    # Сохраняем slug новости для перенаправления
    news_slug = comment.news.slug
    
    # Удаляем комментарий
    comment.delete()
    
    messages.success(request, 'Комментарий успешно удален.')
    return redirect('news:news_detail', slug=news_slug)

@login_required
@require_POST
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.has_user_liked(request.user):
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        # Если пользователь дизлайкнул комментарий, убираем дизлайк
        if comment.has_user_disliked(request.user):
            comment.dislikes.remove(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.get_likes_count(),
        'dislikes_count': comment.get_dislikes_count()
    })

@login_required
@require_POST
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Проверяем, является ли пользователь автором комментария
    if comment.author != request.user:
        return JsonResponse({'error': 'У вас нет прав на редактирование этого комментария'}, status=403)
    
    content = request.POST.get('content')
    if not content:
        return JsonResponse({'error': 'Комментарий не может быть пустым'}, status=400)
    
    comment.content = content
    comment.save()
    
    return JsonResponse({
        'success': True,
        'content': comment.content
    })

@login_required
@require_POST
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.has_user_disliked(request.user):
        comment.dislikes.remove(request.user)
        disliked = False
    else:
        comment.dislikes.add(request.user)
        # Если пользователь лайкнул комментарий, убираем лайк
        if comment.has_user_liked(request.user):
            comment.likes.remove(request.user)
        disliked = True
    
    return JsonResponse({
        'disliked': disliked,
        'dislikes_count': comment.get_dislikes_count(),
        'likes_count': comment.get_likes_count()
    })

@login_required
@require_POST
def like_news(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    if news.has_user_liked(request.user):
        news.likes.remove(request.user)
        liked = False
    else:
        news.likes.add(request.user)
        # Если пользователь дизлайкнул новость, убираем дизлайк
        if news.has_user_disliked(request.user):
            news.dislikes.remove(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': news.get_likes_count(),
        'dislikes_count': news.get_dislikes_count()
    })

@login_required
@require_POST
def dislike_news(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    if news.has_user_disliked(request.user):
        news.dislikes.remove(request.user)
        disliked = False
    else:
        news.dislikes.add(request.user)
        # Если пользователь лайкнул новость, убираем лайк
        if news.has_user_liked(request.user):
            news.likes.remove(request.user)
        disliked = True
    
    return JsonResponse({
        'disliked': disliked,
        'dislikes_count': news.get_dislikes_count(),
        'likes_count': news.get_likes_count()
    })
