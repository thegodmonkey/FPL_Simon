import pandas as pd
import pytest
from api.data_fetcher import get_fbref_stats, get_fpl_data

def test_get_fpl_data():
    """
    Tests the get_fpl_data function.
    """
    # When
    players, teams = get_fpl_data()

    # Then
    assert isinstance(players, list)
    assert isinstance(teams, list)
    assert len(players) > 0
    assert len(teams) > 0

def test_get_fbref_stats():
    """
    Tests the get_fbref_stats function.
    """
    # When
    df = get_fbref_stats(season="2223")

    # Then
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
