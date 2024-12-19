from django.db import models


class Player(models.Model):
    club_id = models.CharField(max_length=50, unique=True)  # Unique identifier
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)  # Store passwords securely in production
    matches_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    win_percentage = models.FloatField(default=0.0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    tournament_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.club_id})"
