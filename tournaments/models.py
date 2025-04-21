from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateField(default=timezone.now)
    country = models.CharField(max_length=2, default='RU')
    game_type = models.CharField(max_length=50, default='CS2')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tournament(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    prize_pool = models.IntegerField(default=0)
    location = models.CharField(max_length=200, default='TBA')
    game_type = models.CharField(max_length=50, default='CS2')
    format = models.CharField(max_length=50, default='Single Elimination')
    teams = models.ManyToManyField(Team, related_name='tournaments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Match(models.Model):
    MATCH_STATUS = (
        ('scheduled', 'Запланирован'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    )

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    score_team1 = models.IntegerField(null=True, blank=True)
    score_team2 = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=MATCH_STATUS, default='scheduled')
    location = models.CharField(max_length=200, default='TBA')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_finished = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'matches'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name}"

    def save(self, *args, **kwargs):
        if self.score_team1 is not None and self.score_team2 is not None:
            self.status = 'completed'
            self.is_finished = True
        super().save(*args, **kwargs)
