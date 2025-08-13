import pytest
import sqlite3
from api.database import init_db, populate_teams_and_players

# Mock data mimicking the FPL API structure
class MockTeam:
    def __init__(self, id, name, code):
        self.id = id
        self.name = name
        self.code = code

class MockPlayer:
    def __init__(self, id, first_name, second_name, element_type, team):
        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.element_type = element_type
        self.team = team

mock_teams_data = [
    MockTeam(id=1, name='Arsenal', code=3),
    MockTeam(id=2, name='Aston Villa', code=7),
]

mock_players_data = [
    MockPlayer(id=1, first_name='Bukayo', second_name='Saka', element_type=3, team=1),
    MockPlayer(id=2, first_name='Ollie', second_name='Watkins', element_type=4, team=2),
    MockPlayer(id=3, first_name='Gabriel', second_name='Magalhães', element_type=2, team=1),
]

def test_populate_database(monkeypatch, tmp_path):
    """
    Tests the database initialization and population.
    """
    # Use a temporary database for this test
    test_db = tmp_path / "test_fpl.db"
    monkeypatch.setattr('api.database.DATABASE_FILE', str(test_db))

    # 1. Initialize the database
    init_db()

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
