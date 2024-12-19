from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_player, name='add_player'),
    path('get/<str:club_id>/', views.get_player, name='get_player'),
    path('update/<str:club_id>/', views.update_player_stats, name='update_player_stats'),
    path('delete/<str:club_id>/', views.delete_player, name='delete_player'),
    path('get_all_players/', views.get_all_players, name='get_all_players'),  # URL pattern for get_all_players
    path('login/', views.login_admin, name='login_admin'),  # New URL pattern for admin login
]