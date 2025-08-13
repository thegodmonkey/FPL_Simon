import pytest
from unittest.mock import MagicMock
from api.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_players(client, mocker):
    """
    Tests the /api/players endpoint.
    """
    # Given
    mock_player_data = [
        {'id': 1, 'name': 'Player 1', 'position': 'FWD'},
        {'id': 2, 'name': 'Player 2', 'position': 'MID'}
    ]

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [dict(row) for row in mock_player_data]
    mock_conn.cursor.return_value = mock_cursor
    # The original app code returns a list of sqlite3.Row objects, which act like dicts.
    # The json conversion is `[dict(player) for player in players]`.
    # `fetchall` should return a list of objects that can be converted to dicts.
    # A list of dicts is the easiest way to mock this.

    # To make the `with conn:` statement work, the mock connection needs __enter__ and __exit__ methods.
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mocker.patch('api.app.get_db_connection', return_value=mock_conn)

    # When
    response = client.get('/api/players')

    # Then
    assert response.status_code == 200
    assert response.json == mock_player_data
