import asyncio
import aiohttp
from fpl import FPL

def get_fpl_player_data():
    """
    Fetches all FPL player data.
    """
    async def fetch_data():
        async with aiohttp.ClientSession() as session:
            fpl = FPL(session)
            players = await fpl.get_players()
            return players

    return asyncio.run(fetch_data())
