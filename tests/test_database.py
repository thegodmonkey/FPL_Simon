import pytest
import sqlite3
import pandas as pd
from api.database import create_database_tables, populate_teams_and_players, populate_fbref_stats, get_player_data

# Mock data mimicking the FPL API structure (as dictionaries)
mock_teams_data = [
    {'id': 1, 'name': 'Arsenal', 'code': 3},
    {'id': 2, 'name': 'Aston Villa', 'code': 7},
]

mock_players_data = [
    {'id': 1, 'first_name': 'Bukayo', 'second_name': 'Saka', 'element_type': 3, 'team': 1},
    {'id': 2, 'first_name': 'Ollie', 'second_name': 'Watkins', 'element_type': 4, 'team': 2},
    {'id': 3, 'first_name': 'Gabriel', 'second_name': 'Magalhães', 'element_type': 2, 'team': 1},
]

def test_populate_database(monkeypatch, tmp_path):
    """
    Tests the database initialization and population.
    """
    # Use a temporary database for this test
    test_db = tmp_path / "test_fpl.db"
    monkeypatch.setattr('api.database.DATABASE_FILE', str(test_db))

    # 1. Initialize the database
    create_database_tables()

    # 2. Populate with mock data
    populate_teams_and_players(mock_players_data, mock_teams_data)

    # 3. Verify the data
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # Check teams
    cursor.execute("SELECT * FROM teams ORDER BY team_id")
    teams = cursor.fetchall()
    assert len(teams) == 2
    assert teams[0] == (1, 'Arsenal', 3)
    assert teams[1] == (2, 'Aston Villa', 7)

    # Check players
    cursor.execute("SELECT * FROM players ORDER BY player_id")
    players = cursor.fetchall()
    assert len(players) == 3

    # Verify specific players to check mapping
    # player_id, full_name, position, team_id
    assert players[0] == (1, 'Bukayo Saka', 'Midfielder', 1)
    assert players[1] == (2, 'Ollie Watkins', 'Forward', 2)
    assert players[2] == (3, 'Gabriel Magalhães', 'Defender', 1)

    conn.close()


def test_populate_fbref_stats(monkeypatch, tmp_path):
    """
    Tests the population of the player_stats_fbref table, including the player_id mapping.
    """
    # Use a temporary database for this test
    test_db = tmp_path / "test_fpl.db"
    monkeypatch.setattr('api.database.DATABASE_FILE', str(test_db))

    # 1. Initialize the database and populate players/teams
    create_database_tables()
    populate_teams_and_players(mock_players_data, mock_teams_data)

    # 2. Create mock fbref stats DataFrame
    fbref_stats_data = {
        'league': ['ENG-Premier League'],
        'season': ['2023-2024'],
        'team': ['Arsenal'],
        'player': ['Bukayo Saka'],
        'Performance_Gls': [10],
        'Performance_Ast': [5],
    }
    stats_df = pd.DataFrame(fbref_stats_data)

    # 3. Populate the fbref stats table
    populate_fbref_stats(stats_df)

    # 4. Verify the data
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row # Ensure we can access columns by name
    cursor = conn.cursor()
    # Query by the mapped player_id (Bukayo Saka's ID is 1)
    cursor.execute("SELECT * FROM player_stats_fbref WHERE player_id = 1")
    stats = cursor.fetchone()

    assert stats is not None
    assert stats['player_id'] == 1
    assert stats['season'] == '2023-2024'
    assert stats['Performance_Gls'] == 10
    assert stats['Performance_Ast'] == 5

    # Verify that a player not in the mapping is ignored
    fbref_stats_data_unmapped = {
        'league': ['ENG-Premier League'],
        'season': ['2023-2024'],
        'team': ['Chelsea'],
        'player': ['Cole Palmer'],
        'Performance_Gls': [22],
        'Performance_Ast': [11],
    }
    stats_df_unmapped = pd.DataFrame(fbref_stats_data_unmapped)
    populate_fbref_stats(stats_df_unmapped)
    cursor.execute("SELECT COUNT(*) FROM player_stats_fbref")
    assert cursor.fetchone()[0] == 1 # Only Bukayo Saka's stats should be there

    conn.close()

def test_get_player_data(monkeypatch, tmp_path):
    """
    Tests the get_player_data function to ensure it correctly joins players and their stats.
    """
    test_db = tmp_path / "test_fpl.db"
    monkeypatch.setattr('api.database.DATABASE_FILE', str(test_db))

    # 1. Setup database
    create_database_tables()
    populate_teams_and_players(mock_players_data, mock_teams_data)
    fbref_stats_data = {
        'league': ['ENG-Premier League'],
        'season': ['2023-2024'],
        'team': ['Arsenal'],
        'player': ['Bukayo Saka'],
        'Performance_Gls': [10],
        'Performance_Ast': [5],
    }
    stats_df = pd.DataFrame(fbref_stats_data)
    populate_fbref_stats(stats_df)

    # 2. Call the function to test
    player_data = get_player_data(player_id=1) # Bukayo Saka

    # 3. Verify the results
    assert not player_data.empty
    assert player_data.iloc[0]['full_name'] == 'Bukayo Saka'
    assert player_data.iloc[0]['Performance_Gls'] == 10
    assert player_data.iloc[0]['Performance_Ast'] == 5
    assert player_data.iloc[0]['player_id'] == 1

    # Test for a player with no stats
    player_data_no_stats = get_player_data(player_id=2) # Ollie Watkins
    assert not player_data_no_stats.empty
    assert player_data_no_stats.iloc[0]['full_name'] == 'Ollie Watkins'
    # Stats columns should be present but contain NaN or None
    assert pd.isna(player_data_no_stats.iloc[0]['Performance_Gls'])
