from rest_framework import serializers

class PlayerSerializer(serializers.Serializer):
    club_id = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)
    matches_played = serializers.IntegerField(default=0)
    wins = serializers.IntegerField(default=0)
    draws = serializers.IntegerField(default=0)
    losses = serializers.IntegerField(default=0)
    win_percentage = serializers.FloatField(default=0.0)
    goals_for = serializers.IntegerField(default=0)
    goals_against = serializers.IntegerField(default=0)
    goal_difference = serializers.IntegerField(default=0)
    tournament_points = serializers.IntegerField(default=0)
