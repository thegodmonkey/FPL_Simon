import asyncio
import aiohttp
from fpl import FPL
from api.database import init_db, populate_teams_and_players

def get_fpl_player_data():
    """
    Fetches all FPL player data and populates the database.
    """
    async def fetch_and_populate():
        async with aiohttp.ClientSession() as session:
            fpl = FPL(session)
            players = await fpl.get_players()
            teams = await fpl.get_teams()

            # Populate database
            init_db()
            populate_teams_and_players(players, teams)

            return players

    return asyncio.run(fetch_and_populate())
