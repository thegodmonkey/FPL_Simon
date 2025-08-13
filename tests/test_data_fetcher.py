import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock
from api.data_fetcher import get_fbref_stats, get_fpl_data


def test_get_fpl_data(mocker):
    """
    Tests the get_fpl_data function with mocks.
    """
    # Given
    mock_fpl_instance = MagicMock()
    mock_fpl_instance.get_players = AsyncMock(return_value=[{'id': 1, 'name': 'Player 1'}])
    mock_fpl_instance.get_teams = AsyncMock(return_value=[{'id': 1, 'name': 'Team 1'}])

    mock_fpl_class = mocker.patch('api.data_fetcher.FPL')
    mock_fpl_class.return_value = mock_fpl_instance

    # When
    players, teams = get_fpl_data()

    # Then
    assert isinstance(players, list)
    assert isinstance(teams, list)
    assert len(players) > 0
    assert len(teams) > 0
    assert players[0]['name'] == 'Player 1'
    assert teams[0]['name'] == 'Team 1'


def test_get_fbref_stats(mocker):
    """
    Tests the get_fbref_stats function with mocks.
    """
    # Given
    mock_df = pd.DataFrame({'player': ['Player 1'], 'goals': [10]})
    mock_fbref_instance = MagicMock()
    mock_fbref_instance.read_player_season_stats.return_value = mock_df

    mock_fbref_class = mocker.patch('api.data_fetcher.sd.FBref')
    mock_fbref_class.return_value = mock_fbref_instance

    # When
    df = get_fbref_stats(season="2223")

    # Then
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.iloc[0]['player'] == 'Player 1'
    mock_fbref_class.assert_called_with(leagues="ENG-Premier League", seasons="2223")
