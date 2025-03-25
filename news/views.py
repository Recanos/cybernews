from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import News, Category, Tag, Comment
from .forms import CommentForm

def news_list(request, category_slug=None, tag_slug=None):
    news_list = News.objects.filter(is_published=True)
    
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
    })

def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    comments = news.comments.filter(is_approved=True)
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.news = news
            comment.author = request.user
            comment.save()
            messages.success(request, 'Ваш комментарий отправлен на модерацию.')
            return redirect('news:news_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    return render(request, 'news/news_detail.html', {
        'news': news,
        'comments': comments,
        'comment_form': comment_form,
    })

@login_required
def add_comment(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.news = news
            comment.author = request.user
            comment.save()
            messages.success(request, 'Ваш комментарий отправлен на модерацию.')
            return redirect('news:news_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    return render(request, 'news/add_comment.html', {
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
