import asyncio
import aiohttp
from fpl import FPL
import soccerdata as sd
import pandas as pd

def get_fpl_data():
    """
    Fetches all FPL player and team data.
    """
    async def fetch_data():
        async with aiohttp.ClientSession() as session:
            fpl = FPL(session)
            players = await fpl.get_players(return_json=True)
            teams = await fpl.get_teams(return_json=True)
            return players, teams

    return asyncio.run(fetch_data())

def get_fbref_stats(season: str) -> pd.DataFrame:
    """
    Fetches player season stats from FBref.
    """
    fbref = sd.FBref(leagues="ENG-Premier League", seasons=season)
    df = fbref.read_player_season_stats()
    return df
