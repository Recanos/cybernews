from django import forms
from .models import Tournament, Match, Team

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'description', 'start_date', 'end_date', 'location', 'prize_pool', 'format', 'game_type']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'location': 'Место проведения',
            'prize_pool': 'Призовой фонд',
            'format': 'Формат',
            'game_type': 'Игра'
        }

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['start_time', 'end_time', 'team1', 'team2', 'score_team1', 'score_team2', 'status']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'start_time': 'Время начала',
            'end_time': 'Время окончания',
            'team1': 'Команда 1',
            'team2': 'Команда 2',
            'score_team1': 'Счет команды 1',
            'score_team2': 'Счет команды 2',
            'status': 'Статус'
        }

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament', None)
        super().__init__(*args, **kwargs)
        
        if tournament:
            # Фильтруем команды только из участников турнира
            tournament_teams = tournament.teams.all()
            self.fields['team1'].queryset = tournament_teams
            self.fields['team2'].queryset = tournament_teams
            
            # Добавляем пустой выбор для статуса
            self.fields['status'].choices = [
                ('', '---------'),
                ('scheduled', 'Запланирован'),
                ('in_progress', 'В процессе'),
                ('completed', 'Завершен'),
                ('cancelled', 'Отменен')
            ]
        else:
            self.fields['team1'].queryset = Team.objects.none()
            self.fields['team2'].queryset = Team.objects.none()

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'created_at', 'country', 'players_count', 'rating', 'wins', 'logo']
        labels = {
            'name': 'Название команды',
            'description': 'Описание',
            'created_at': 'Дата создания',
            'country': 'Страна',
            'players_count': 'Количество игроков',
            'rating': 'Рейтинг',
            'wins': 'Победы',
            'logo': 'Логотип'
        }
        widgets = {
            'created_at': forms.DateInput(attrs={'type': 'date'})
        } 