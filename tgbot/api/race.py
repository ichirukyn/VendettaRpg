from aiohttp import ClientSession

from tgbot.api._config import url
from tgbot.models.api.class_api import ClassType
from tgbot.models.api.race_api import RaceBonusType
from tgbot.models.api.race_api import RaceType


async def get_race(session, race_id: int) -> RaceType | None:
    async with session.get(url(f'/race/{race_id}')) as res:
        if res.status == 200:
            return await res.json()

        return None


async def fetch_race(session: ClientSession) -> [RaceType]:
    async with session.get(url(f'/race'), params={'hidden': 'false'}) as res:
        return await res.json()


async def fetch_race_bonuses(session, race_id: int) -> [RaceBonusType]:
    async with session.get(url(f'/race/{race_id}/effect')) as res:
        return await res.json()


async def fetch_race_classes(session, race_id) -> [ClassType]:
    async with session.get(url(f'/race/{race_id}/class')) as res:
        return await res.json()
