from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Tournament, Team, Match
from .forms import TournamentForm, MatchForm, TeamForm
from datetime import datetime
from django.utils.text import slugify
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

# Tournament views
def tournament_list(request):
    active_tournaments = Tournament.objects.filter(is_active=True)
    upcoming_tournaments = active_tournaments.filter(start_date__gt=datetime.now())
    current_tournaments = active_tournaments.filter(
        start_date__lte=datetime.now(),
        end_date__gte=datetime.now()
    )
    past_tournaments = active_tournaments.filter(end_date__lt=datetime.now())
    
    return render(request, 'tournaments/tournament_list.html', {
        'upcoming_tournaments': upcoming_tournaments,
        'current_tournaments': current_tournaments,
        'past_tournaments': past_tournaments,
    })

def tournament_detail(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = tournament.matches.all().order_by('start_time')
    
    active_tournaments = Tournament.objects.filter(
        is_active=True,
        start_date__lte=datetime.now(),
        end_date__gte=datetime.now()
    )
    
    # Получаем все команды для возможности добавления в турнир
    teams = Team.objects.all()
    
    return render(request, 'tournaments/tournament_detail.html', {
        'tournament': tournament,
        'matches': matches,
        'active_tournaments': active_tournaments,
        'active_teams': teams,  # Передаем все команды в контекст
    })

@login_required
@user_passes_test(is_staff_user)
def create_tournament(request):
    if request.method == 'POST':
        form = TournamentForm(request.POST, request.FILES)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.is_active = True
            # Генерируем slug из названия турнира с транслитерацией
            tournament.slug = transliterate(tournament.name)
            tournament.save()
            messages.success(request, 'Турнир успешно создан')
            return redirect('tournaments:tournament_detail', pk=tournament.pk)
    else:
        form = TournamentForm()
    return render(request, 'tournaments/tournament_form.html', {'form': form, 'title': 'Создать турнир'})

@login_required
@user_passes_test(is_staff_user)
def edit_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        form = TournamentForm(request.POST, request.FILES, instance=tournament)
        if form.is_valid():
            tournament = form.save(commit=False)
            # Обновляем slug при изменении названия
            tournament.slug = transliterate(tournament.name)
            tournament.save()
            messages.success(request, 'Турнир успешно обновлен.')
            return redirect('tournaments:tournament_detail', pk=tournament.pk)
    else:
        form = TournamentForm(instance=tournament)
    
    return render(request, 'tournaments/tournament_form.html', {
        'form': form,
        'tournament': tournament,
        'title': 'Редактирование турнира'
    })

@login_required
@user_passes_test(is_staff_user)
def delete_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        tournament.delete()
        messages.success(request, 'Турнир успешно удален.')
        return redirect('tournaments:tournament_list')
    return redirect('tournaments:tournament_detail', pk=tournament.pk)

# Team views
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    upcoming_matches = team.home_matches.filter(
        start_time__gt=datetime.now(),
        is_finished=False
    ) | team.away_matches.filter(
        start_time__gt=datetime.now(),
        is_finished=False
    )
    past_matches = team.home_matches.filter(
        is_finished=True
    ) | team.away_matches.filter(
        is_finished=True
    )
    
    return render(request, 'tournaments/team_detail.html', {
        'team': team,
        'upcoming_matches': upcoming_matches,
        'past_matches': past_matches,
    })

@login_required
@user_passes_test(is_staff_user)
def create_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save(commit=False)
            # Генерируем slug из названия команды с транслитерацией
            team.slug = transliterate(team.name)
            team.save()
            messages.success(request, 'Команда успешно создана.')
            return redirect('tournaments:team_detail', pk=team.pk)
    else:
        form = TeamForm()
    
    return render(request, 'tournaments/team_form.html', {
        'form': form,
        'title': 'Создание команды'
    })

@login_required
@user_passes_test(is_staff_user)
def edit_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            team = form.save(commit=False)
            # Обновляем slug при изменении названия
            team.slug = transliterate(team.name)
            team.save()
            messages.success(request, 'Команда успешно обновлена.')
            return redirect('tournaments:team_detail', pk=team.pk)
    else:
        form = TeamForm(instance=team)
    
    return render(request, 'tournaments/team_form.html', {
        'form': form,
        'team': team,
        'title': 'Редактирование команды'
    })

@login_required
@user_passes_test(is_staff_user)
def delete_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        team.delete()
        messages.success(request, 'Команда успешно удалена.')
        return redirect('tournaments:tournament_list')
    return redirect('tournaments:team_detail', pk=team.pk)

# Match views
@login_required
@user_passes_test(is_staff_user)
def create_match(request):
    tournament_pk = request.GET.get('tournament')
    if not tournament_pk:
        messages.error(request, 'Не указан турнир для создания матча.')
        return redirect('tournaments:tournament_list')
    
    tournament = get_object_or_404(Tournament, pk=tournament_pk)
    
    if request.method == 'POST':
        form = MatchForm(request.POST, tournament=tournament)
        if form.is_valid():
            match = form.save(commit=False)
            match.tournament = tournament
            match.save()
            messages.success(request, 'Матч успешно создан.')
            return redirect('tournaments:tournament_detail', pk=tournament.pk)
    else:
        form = MatchForm(tournament=tournament)
    
    return render(request, 'tournaments/match_form.html', {
        'form': form,
        'tournament': tournament,
        'title': 'Создание матча'
    })

@login_required
@user_passes_test(is_staff_user)
def edit_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    tournament = match.tournament
    
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match, tournament=tournament)
        if form.is_valid():
            form.save()
            messages.success(request, 'Матч успешно обновлен.')
            return redirect('tournaments:tournament_detail', pk=tournament.pk)
    else:
        form = MatchForm(instance=match, tournament=tournament)
    
    return render(request, 'tournaments/match_form.html', {
        'form': form,
        'match': match,
        'tournament': tournament,
        'title': 'Редактирование матча'
    })

@login_required
@user_passes_test(is_staff_user)
def delete_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    tournament_pk = match.tournament.pk
    if request.method == 'POST':
        match.delete()
        messages.success(request, 'Матч успешно удален.')
        return redirect('tournaments:tournament_detail', pk=tournament_pk)
    
    return render(request, 'tournaments/match_confirm_delete.html', {
        'match': match
    })

@login_required
@user_passes_test(is_staff_user)
def add_team_to_tournament(request, tournament_pk, team_pk):
    tournament = get_object_or_404(Tournament, pk=tournament_pk)
    team = get_object_or_404(Team, pk=team_pk)
    
    if request.method == 'POST':
        tournament.teams.add(team)
        messages.success(request, f'Команда {team.name} добавлена в турнир.')
    
    return redirect('tournaments:tournament_detail', pk=tournament.pk)

@login_required
@user_passes_test(is_staff_user)
def remove_team_from_tournament(request, tournament_pk, team_pk):
    tournament = get_object_or_404(Tournament, pk=tournament_pk)
    team = get_object_or_404(Team, pk=team_pk)
    
    if request.method == 'POST':
        tournament.teams.remove(team)
        messages.success(request, f'Команда {team.name} удалена из турнира.')
    
    return redirect('tournaments:tournament_detail', pk=tournament.pk)
