from rest_framework.response import Response
from rest_framework.decorators import api_view
from firebase_admin import firestore
from .serializers import PlayerSerializer
from datetime import datetime
# Initialize Firestore
db = firestore.client()

@api_view(['POST'])
def login_admin(request):
    """
    Authenticate an admin user based on username and password.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=400)

    # Query the 'admins' collection for the provided username
    admins_ref = db.collection('admins')
    query = admins_ref.where('username', '==', username).stream()

    # Convert query results to a list
    admin_docs = list(query)
    if not admin_docs:
        return Response({'error': 'Invalid username or password.'}, status=401)

    # Assuming usernames are unique, retrieve the first match
    admin_data = admin_docs[0].to_dict()

    # Validate the password
    if admin_data['password'] == password:
        return Response({'message': 'Login successful', 'username': username})
    else:
        return Response({'error': 'Invalid username or password.'}, status=401)
# Add a Player
@api_view(['POST'])
def add_player(request):
    serializer = PlayerSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        # Save to Firestore
        db.collection('players').document(data['club_id']).set(data)
        return Response({'message': 'Player added successfully'})
    return Response(serializer.errors, status=400)

# Get a Player
@api_view(['GET'])
def get_player(request, club_id):
    player_ref = db.collection('players').document(club_id).get()
    if player_ref.exists:
        return Response(player_ref.to_dict())
    return Response({'error': 'Player not found'}, status=404)

# Get All Players
@api_view(['GET'])
def get_all_players(request):
    players_ref = db.collection('players').stream()
    players = [player.to_dict() for player in players_ref]

    if players:
        return Response(players)
    return Response({'message': 'No players found'}, status=404)

# Update Player Stats
@api_view(['POST'])
def update_player_stats(request, club_id):
    player_ref = db.collection('players').document(club_id)
    player = player_ref.get()

    if player.exists:
        player_data = player.to_dict()
        stats = request.data

        # Validate input
        result = stats.get('result')  # Expected: 'win', 'draw', 'loss'
        goals_for = stats.get('goals_for', 0)
        goals_against = stats.get('goals_against', 0)
        motm = stats.get('motm', False)

        if result not in ['win', 'draw', 'loss']:
            return Response({'error': 'Invalid result value. Must be "win", "draw", or "loss".'}, status=400)

        if not isinstance(goals_for, int) or not isinstance(goals_against, int):
            return Response({'error': 'Goals must be integers'}, status=400)

        # Get current month
        current_month = datetime.now().strftime('%Y-%m')
        monthly_ref = db.collection(f'players_monthly/{current_month}/records').document(club_id)
        monthly = monthly_ref.get()

        # Initialize monthly stats if they don't exist
        if not monthly.exists:
            monthly_data = {
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'matches_played': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'tournament_points': 0,
                'win_percentage': 0,
            }
        else:
            monthly_data = monthly.to_dict()

        # Update statistics for both overall and monthly
        for data in [player_data, monthly_data]:
            if result == 'win':
                data['wins'] += 1
                data['tournament_points'] += 3
            elif result == 'draw':
                data['draws'] += 1
                data['tournament_points'] += 1
            elif result == 'loss':
                data['losses'] += 1

            data['matches_played'] += 1
            data['goals_for'] += goals_for
            data['goals_against'] += goals_against
            data['goal_difference'] = data['goals_for'] - data['goals_against']

            if motm:
                data['tournament_points'] += 2

            # Avoid zero division
            data['win_percentage'] = (
                (data['wins'] / data['matches_played']) * 100
                if data['matches_played'] > 0
                else 0
            )

        # Save updated stats
        player_ref.set(player_data)
        monthly_ref.set(monthly_data)

        return Response({
            'message': 'Player stats updated successfully',
            'player_data': player_data,
            'monthly_data': monthly_data
        })

    return Response({'error': 'Player not found'}, status=404)

# Delete a Player
@api_view(['DELETE'])
def delete_player(request, club_id):
    player_ref = db.collection('players').document(club_id)
    if player_ref.get().exists:
        player_ref.delete()
        return Response({'message': 'Player deleted successfully'})
    return Response({'error': 'Player not found'}, status=404)
@api_view(['GET'])
def get_monthly_report(request, month, club_id=None):
    """
    Retrieve monthly stats for all players or a specific player for a given month.
    """
    monthly_ref = db.collection(f'players_monthly_{month}')

    if club_id:
        # Fetch stats for a specific player
        player_ref = monthly_ref.document(club_id).get()
        if player_ref.exists:
            return Response(player_ref.to_dict())
        return Response({'error': f'Player with club_id {club_id} not found for month {month}.'}, status=404)

    # Fetch stats for all players
    players_ref = monthly_ref.stream()
    players = [player.to_dict() for player in players_ref]

    if players:
        return Response(players)
    return Response({'message': f'No players found for month {month}.'}, status=404)
@api_view(['POST'])
def reset_monthly_stats(request):
    """
    Reset monthly stats for all players at the start of a new month.
    """
    # Get the current month
    current_month = datetime.now().strftime('%Y-%m')
    monthly_ref = db.collection(f'players_monthly/{current_month}/records')

    # Fetch all players in the main 'players' collection
    players_ref = db.collection('players').stream()
    players = [player.to_dict() for player in players_ref]

    for player in players:
        club_id = player['club_id']
        monthly_data = {
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'matches_played': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0,
            'tournament_points': 0,
            'win_percentage': 0,
        }
        # Save new monthly stats
        monthly_ref.document(club_id).set(monthly_data)

    return Response({'message': f'Monthly stats reset for all players for {current_month}.'})
