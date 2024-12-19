from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        "club_id",
        "name",
        "matches_played",
        "wins",
        "draws",
        "losses",
        "win_percentage",
        "goals_for",
        "goals_against",
        "goal_difference",
        "tournament_points",
    )
    search_fields = ["name", "club_id"]  # Add a search field in the admin
    list_filter = ["wins", "losses", "draws"]  # Add filtering options
