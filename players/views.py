from rest_framework.response import Response
from rest_framework.decorators import api_view
from firebase_admin import firestore
from .serializers import PlayerSerializer
from datetime import datetime, timedelta

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

        # Save to the main `players` table
        db.collection('players').document(data['club_id']).set(data)

        # Check and create the current month's table if not exists
        current_month = datetime.now().strftime('%Y-%m')
        current_month_table = f'players_monthly_{current_month}'
        current_month_ref = db.collection(current_month_table)

        # If the table doesn't exist, create it
        players_ref = current_month_ref.stream()
        if not list(players_ref):
            create_new_month_table(request)

        # Add player stats for the current month
        monthly_data = {
            'name': data['name'],
            'club_id': data['club_id'],
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
        db.collection(current_month_table).document(data['club_id']).set(monthly_data)

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
        month = stats.get('month')  # Month should come from frontend

        if not month:
            return Response({'error': 'Month is required.'}, status=400)

        # Ensure month is formatted as 'YYYY-MM'
        try:
            month = datetime.strptime(month, '%Y-%m').strftime('%Y-%m')
        except ValueError:
            return Response({'error': 'Invalid month format. Use YYYY-MM.'}, status=400)

        current_month_table = f'players_monthly_{month}'
        monthly_ref = db.collection(current_month_table).document(club_id)

        # If the table doesn't exist, create it
        current_month_ref = db.collection(current_month_table)
        players_ref = current_month_ref.stream()
        if not list(players_ref):
            create_new_month_table(request)

        # Get the current month's player stats
        monthly = monthly_ref.get()

        if not monthly.exists:
            monthly_data = {
                'name': player_data.get('name', ''),
                'club_id': player_data.get('id', ''),
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


@api_view(['DELETE'])
def delete_player(request, club_id):
    # Delete from the main `players` table
    player_ref = db.collection('players').document(club_id)
    if player_ref.get().exists:
        player_ref.delete()

        # Check and create the current month's table if not exists
        current_month = datetime.now().strftime('%Y-%m')
        current_month_table = f'players_monthly_{current_month}'
        current_month_ref = db.collection(current_month_table)

        # If the table doesn't exist, create it
        players_ref = current_month_ref.stream()
        if not list(players_ref):
            create_new_month_table(request)

        # Delete from the current month's table
        monthly_ref = db.collection(current_month_table).document(club_id)
        if monthly_ref.get().exists:
            monthly_ref.delete()

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
def reset_monthly_data(request):
    """
    Reset all player stats for the current month. If the table for the current month does not exist,
    delete the previous month's table and create a new table for the current month.
    """
    # Get the current and previous months
    current_month = datetime.now().strftime('%Y-%m')
    previous_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

    # Reference for current and previous month tables
    current_month_table = f'players_monthly_{current_month}'
    previous_month_table = f'players_monthly_{previous_month}'

    current_month_ref = db.collection(current_month_table)
    previous_month_ref = db.collection(previous_month_table)

    # Check if the current month's table exists
    players_ref = current_month_ref.stream()
    players_list = list(players_ref)

    if not players_list:
        # If the current month's table does not exist, delete the previous month's table
        previous_players_ref = previous_month_ref.stream()
        for player in previous_players_ref:
            previous_month_ref.document(player.id).delete()

        # Initialize a new table for the current month
        return Response({
            'message': f'Previous table "{previous_month_table}" deleted. New table "{current_month_table}" created for the current month.'
        })

    # Reset data for the current month
    updated_count = 0
    for player in players_list:
        player_data = player.to_dict()

        # Preserve name and id, reset other stats
        reset_data = {
            'name': player_data.get('name', ''),
            'club_id': player_data.get('id', ''),
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

        # Update the document with reset data
        current_month_ref.document(player.id).set(reset_data)
        updated_count += 1

    return Response({
        'message': f'Reset successful for {updated_count} players in table "{current_month_table}".',
    })
@api_view(['POST'])
def create_new_month_table(request):
    """
    Create a new table for the current month.
    If the table for the month before the previous month exists, remove its documents.
    The table for the current month is created if it doesn't already exist.
    """
    current_month = datetime.now().strftime('%Y-%m')
    current_month_table = f'players_monthly_{current_month}'

    # Calculate the month before the previous month
    first_of_current_month = datetime.now().replace(day=1)
    previous_month = first_of_current_month - timedelta(days=1)
    before_previous_month = (previous_month.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

    before_previous_month_table = f'players_monthly_{before_previous_month}'

    # Check and delete documents from the before previous month's table if it exists
    before_previous_month_ref = db.collection(before_previous_month_table)
    docs = before_previous_month_ref.stream()

    for doc in docs:
        doc.reference.delete()  # Delete each document inside the collection

    print(f"All documents in {before_previous_month_table} deleted.")

    # Check if the current month's table exists
    current_month_ref = db.collection(current_month_table)
    players_ref = current_month_ref.stream()
    players_list = list(players_ref)

    if players_list:
        return Response({'message': f'Table for {current_month} already exists.'}, status=200)

    # Create the table for the current month and add initial player data
    players_ref = db.collection('players').stream()
    players = [player.to_dict() for player in players_ref]

    for player in players:
        # Initialize new player stats for the month
        monthly_data = {
            'name': player['name'],
            'club_id': player['club_id'],
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
        current_month_ref.document(player['club_id']).set(monthly_data)

    return Response({'message': f'New table for {current_month} created successfully.'})
