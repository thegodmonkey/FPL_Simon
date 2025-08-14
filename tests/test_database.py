import pytest
import sqlite3
import pandas as pd
from api.database import create_database_tables, populate_teams_and_players, populate_fbref_stats

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
    Tests the population of the player_stats_fbref table with a wide range of stats.
    """
    # Use a temporary database for this test
    test_db = tmp_path / "test_fpl.db"
    monkeypatch.setattr('api.database.DATABASE_FILE', str(test_db))

    # 1. Initialize the database and populate players/teams
    create_database_tables()
    populate_teams_and_players(mock_players_data, mock_teams_data)

    # 2. Create mock fbref stats DataFrame
    fbref_stats_data = {
        'player_id': [1],
        'season': ['2023-2024'],
        'minutes_per_90': [28.3],
        'xg_per_90': [0.45],
        'xa_per_90': [0.21],
        'goals': [10],
        'assists': [5],
        'sh': [50],
        'sot': [25],
        'cmp': [1000],
        'att_pass': [1200],
        'sca': [100],
        'gca': [10],
        'tkl': [30],
        'tklw': [20],
        'touches': [2000],
        'succ_dribbles': [40],
        'att_dribbles': [60],
        'crdy_misc': [5],
        'crdr_misc': [1]
    }
    stats_df = pd.DataFrame(fbref_stats_data)

    # 3. Populate the fbref stats table
    populate_fbref_stats(stats_df)

    # 4. Verify the data
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row # Ensure we can access columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM player_stats_fbref WHERE player_id = 1")
    stats = cursor.fetchone()

    assert stats is not None

    # Verify a subset of the columns
    assert stats['player_id'] == 1
    assert stats['season'] == '2023-2024'
    assert stats['goals'] == 10
    assert stats['assists'] == 5
    assert stats['sh'] == 50
    assert stats['sot'] == 25
    assert stats['cmp'] == 1000
    assert stats['att_pass'] == 1200
    assert stats['sca'] == 100
    assert stats['gca'] == 10
    assert stats['tkl'] == 30
    assert stats['tklw'] == 20
    assert stats['touches'] == 2000
    assert stats['succ_dribbles'] == 40
    assert stats['att_dribbles'] == 60
    assert stats['crdy_misc'] == 5
    assert stats['crdr_misc'] == 1

    conn.close()
