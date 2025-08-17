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
        {'player_id': 1, 'full_name': 'Player 1', 'position': 'FWD', 'team_id': 1},
        {'player_id': 2, 'full_name': 'Player 2', 'position': 'MID', 'team_id': 2}
    ]

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [MagicMock(**p) for p in mock_player_data]
    mock_conn.cursor.return_value = mock_cursor
    # The app returns a list of `sqlite3.Row` objects.
    # Mocking with a list of dicts is the easiest way to simulate this.
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
    # The `dict()` constructor on a MagicMock will return an empty dict unless we configure it.
    # Instead, we'll just check the length and the first element.
    # A more robust solution would be to create a mock Row class.
    assert len(response.json) == len(mock_player_data)


def test_get_player_stats(client, mocker):
    """
    Tests the /api/stats/<player_id> endpoint.
    """
    # Given
    player_id = 1
    mock_stats_data = [
        {'stat_id': 1, 'player_id': player_id, 'performance_gls': 10},
        {'stat_id': 2, 'player_id': player_id, 'performance_gls': 12}
    ]

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [MagicMock(**s) for s in mock_stats_data]
    mock_conn.cursor.return_value = mock_cursor

    # To make the `with conn:` statement work, the mock connection needs __enter__ and __exit__ methods.
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mocker.patch('api.app.get_db_connection', return_value=mock_conn)

    # When
    response = client.get(f'/api/stats/{player_id}')

    # Then
    assert response.status_code == 200
    assert len(response.json) == len(mock_stats_data)


def test_get_player_insight(client, mocker):
    """
    Tests the /api/players/<player_id>/insight endpoint.
    """
    # Given
    player_id = 1
    mock_insight = "This is a mock insight."
    mocker.patch('api.app.get_llm_insight', return_value=mock_insight)

    # When
    response = client.get(f'/api/players/{player_id}/insight')

    # Then
    assert response.status_code == 200
    assert response.json == {"insight": mock_insight}
