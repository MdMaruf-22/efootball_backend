from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_player, name='add_player'),
    path('get/<str:club_id>/', views.get_player, name='get_player'),
    path('update/<str:club_id>/', views.update_player_stats, name='update_player_stats'),
    path('delete/<str:club_id>/', views.delete_player, name='delete_player'),
    path('get_all_players/', views.get_all_players, name='get_all_players'),  # URL pattern for get_all_players
    path('login/', views.login_admin, name='login_admin'),  # URL pattern for admin login

    # New endpoints for monthly report and reset
    path('monthly_report/<str:month>/', views.get_monthly_report, name='get_monthly_report_all'),
    path('monthly_report/<str:month>/<str:club_id>/', views.get_monthly_report, name='get_monthly_report_player'),
    path('reset_monthly_stats/', views.reset_monthly_data, name='reset_monthly_stats'),
]
