import aiohttp

from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.hero_api import CreateHeroType
from tgbot.models.api.hero_api import HeroLvlType
from tgbot.models.api.hero_api import HeroStatsType
from tgbot.models.api.hero_api import HeroType


async def create_hero(body: CreateHeroType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/hero'), json=body)
        return await res.json()


async def get_hero(session, hero_id: int, user_id: int) -> Response[HeroType]:
    res = await session.get(url(f'/hero/{str(hero_id)}'), params={'user_id': user_id})
    return Response(res, HeroType)


async def get_hero_stats(session, hero_id) -> [HeroStatsType]:
    res = await session.get(url(f'/hero/{hero_id}/stats'))
    return await res.json()


async def get_hero_lvl(session, hero_id) -> Response[HeroLvlType]:
    res = await session.get(url(f'/hero/{hero_id}/lvl'))
    return Response(res, HeroLvlType)


async def fetch_hero(session, ) -> [HeroType]:
    res = await session.get(url(f'/hero'))
    return await res.json()
