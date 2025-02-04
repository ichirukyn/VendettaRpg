import aiohttp

from tgbot.api.class_ import fetch_class
from tgbot.api.race import fetch_race
from tgbot.api.technique import fetch_techniques


async def fetch():
    session = aiohttp.ClientSession()

    races = await fetch_race(session)
    classes = await fetch_class(session)
    techniques = await fetch_techniques(session)

    await session.close()

    return races, classes, techniques
