from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.class_api import ClassType
from tgbot.models.api.race_api import RaceBonusType
from tgbot.models.api.race_api import RaceType


async def get_race(session, race_id: int) -> Response[RaceType]:
    res = await session.get(url(f'/race/{race_id}'))
    return Response(res, RaceType)


async def fetch_race(session) -> [RaceType]:
    res = await session.get(url(f'/race'))
    return await res.json()


async def fetch_race_bonuses(session, race_id: int) -> [RaceBonusType]:
    res = await session.get(url(f'/race/{race_id}/effect'))
    return await res.json()


async def fetch_race_classes(session, race_id) -> [ClassType]:
    res = await session.get(url(f'/race/{race_id}/class'))
    return await res.json()
