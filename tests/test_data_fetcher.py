import pandas as pd
import pytest
from api.data_fetcher import get_fbref_stats

def test_get_fbref_stats():
    """
    Tests the get_fbref_stats function.
    """
    # When
    df = get_fbref_stats(season="2223")

    # Then
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
