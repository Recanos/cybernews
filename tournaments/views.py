from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Tournament, Team, Match
from datetime import datetime

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

def tournament_detail(request, slug):
    tournament = get_object_or_404(Tournament, slug=slug)
    matches = tournament.matches.all().order_by('start_time')
    
    return render(request, 'tournaments/tournament_detail.html', {
        'tournament': tournament,
        'matches': matches,
    })

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

def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    
    return render(request, 'tournaments/match_detail.html', {
        'match': match,
    })

def match_schedule(request):
    upcoming_matches = Match.objects.filter(
        start_time__gt=datetime.now(),
        is_finished=False
    ).order_by('start_time')
    
    paginator = Paginator(upcoming_matches, 10)
    page = request.GET.get('page')
    matches = paginator.get_page(page)
    
    return render(request, 'tournaments/match_schedule.html', {
        'matches': matches,
    })

def match_results(request):
    past_matches = Match.objects.filter(
        is_finished=True
    ).order_by('-end_time')
    
    paginator = Paginator(past_matches, 10)
    page = request.GET.get('page')
    matches = paginator.get_page(page)
    
    return render(request, 'tournaments/match_results.html', {
        'matches': matches,
    })
