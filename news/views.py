from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from .models import News, Category, Tag, Comment
from .forms import CommentForm, NewsForm, CategoryForm, TagForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from django.utils.text import slugify
from django.utils.dateformat import format as date_format
import uuid
from django.utils.timezone import localtime
from django.db.models import Count, F, ExpressionWrapper, IntegerField
import re

def transliterate(text):
    """Транслитерация русского текста в латиницу"""
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    # Заменяем русские буквы на латинские
    for cyr, lat in translit_dict.items():
        text = text.replace(cyr, lat)

    # Заменяем все символы, кроме букв и цифр, на дефис
    text = re.sub(r'[^a-zA-Z0-9]', '-', text)

    # Удаляем множественные дефисы
    text = re.sub(r'-+', '-', text)

    # Удаляем дефисы в начале и конце
    text = text.strip('-')

    return text.lower()

def is_staff_user(user):
    return user.is_staff or user.is_superuser

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

    sort_news = request.GET.get('sort_news', 'newest')
    if sort_news == 'oldest':
        news_list = news_list.order_by('created_at')
    elif sort_news == 'popular_views':
        news_list = news_list.order_by('-views_count', '-created_at')
    elif sort_news == 'popular_comments':
        news_list = news_list.annotate(comments_count=Count('comments')).order_by('-comments_count', '-created_at')
    elif sort_news == 'popular':
        news_list = news_list.annotate(
            likes_count=Count('likes'),
            dislikes_count=Count('dislikes'),
            popularity_score=ExpressionWrapper(F('likes_count') - F('dislikes_count'), output_field=IntegerField())
        ).order_by('-popularity_score', '-created_at')
    else:  # newest
        news_list = news_list.order_by('-created_at')
    
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
        'sort_news': sort_news,
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
    
    # Проверяем, что пользователь является автором комментария или имеет права администратора/модератора
    if comment.author != request.user and not (request.user.is_staff or request.user.is_superuser):
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
        'content': comment.content,
        'updated_at': date_format(localtime(comment.updated_at), 'd.m.Y H:i'),
        'created_at': date_format(localtime(comment.created_at), 'd.m.Y H:i'),
        'is_edited': (comment.updated_at - comment.created_at).total_seconds() > 1
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

@login_required
@user_passes_test(is_staff_user)
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            # Генерируем уникальный slug
            base_slug = slugify(news.title)
            unique_slug = base_slug
            counter = 1
            # Проверяем, существует ли новость с таким slug
            while News.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            news.slug = unique_slug
            news.is_published = True
            news.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Новость успешно опубликована!')
            return redirect('news:news_detail', slug=news.slug)
    else:
        form = NewsForm()
    
    return render(request, 'news/news_form.html', {
        'form': form,
        'title': 'Создать новость',
        'button_text': 'Создать'
    })

@login_required
@user_passes_test(is_staff_user)
def edit_news(request, slug):
    news = get_object_or_404(News, slug=slug)
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            news = form.save()
            messages.success(request, 'Новость успешно обновлена!')
            return redirect('news:news_detail', slug=news.slug)
    else:
        form = NewsForm(instance=news)
    
    return render(request, 'news/news_form.html', {
        'form': form,
        'news': news,
        'title': 'Редактировать новость',
        'button_text': 'Сохранить'
    })

@login_required
@user_passes_test(is_staff_user)
@require_POST
def delete_news(request, slug):
    news = get_object_or_404(News, slug=slug)
    news.delete()
    messages.success(request, 'Новость успешно удалена!')
    return redirect('news:news_list')

@require_POST
def create_category(request):
    name = request.POST.get('name')
    if not name:
        return JsonResponse({'success': False, 'error': 'Название обязательно'})
    category, created = Category.objects.get_or_create(name=name)
    if created:
        category.save()
    return JsonResponse({'success': True, 'id': category.id, 'name': category.name, 'slug': category.slug})

@require_POST
def create_tag(request):
    name = request.POST.get('name')
    if not name:
        return JsonResponse({'success': False, 'error': 'Название обязательно'})
    tag, created = Tag.objects.get_or_create(name=name)
    if created:
        tag.save()
    return JsonResponse({'success': True, 'id': tag.id, 'name': tag.name, 'slug': tag.slug})

@login_required
@user_passes_test(is_staff_user)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = transliterate(category.name)
            category.save()
            messages.success(request, 'Категория успешно обновлена.')
            return redirect('news:news_list') # Redirect back to news list
    else:
        form = CategoryForm(instance=category)
    return render(request, 'news/category_form.html', {'form': form, 'title': 'Редактировать категорию'})

@login_required
@user_passes_test(is_staff_user)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Категория "{category.name}" успешно удалена.')
    return redirect('news:news_list') # Always redirect back to news list

@login_required
@user_passes_test(is_staff_user)
def edit_tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.slug = transliterate(tag.name)
            tag.save()
            messages.success(request, 'Тег успешно обновлен.')
            return redirect('news:news_list') # Redirect back to news list
    else:
        form = TagForm(instance=tag)
    return render(request, 'news/tag_form.html', {'form': form, 'title': 'Редактировать тег'})

@login_required
@user_passes_test(is_staff_user)
def delete_tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == 'POST':
        tag.delete()
        messages.success(request, f'Тег "{tag.name}" успешно удален.')
    return redirect('news:news_list') # Always redirect back to news list
