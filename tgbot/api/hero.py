import aiohttp

from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.hero_api import CreateHeroType
from tgbot.models.api.hero_api import HeroLvlType
from tgbot.models.api.hero_api import HeroStatsType
from tgbot.models.api.hero_api import HeroTechniqueType
from tgbot.models.api.hero_api import HeroType


async def create_hero(body: CreateHeroType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/hero'), json=body)
        return await res.json()


async def get_hero(session, hero_id: int, user_id: int) -> Response[HeroType]:
    res = await session.get(url(f'/hero/{str(hero_id)}'), params={'user_id': user_id})
    return Response(res, HeroType)


async def fetch_hero(session, ) -> [HeroType]:
    res = await session.get(url(f'/hero'))
    return await res.json()


# Stats
async def get_hero_stats(session, hero_id) -> [HeroStatsType]:
    res = await session.get(url(f'/hero/{hero_id}/stats'))
    return await res.json()


# Lvl
async def get_hero_lvl(session, hero_id) -> Response[HeroLvlType]:
    res = await session.get(url(f'/hero/{hero_id}/lvl'))
    return Response(res, HeroLvlType)


# Technique
async def fetch_hero_technique(session, hero_id) -> Response[HeroTechniqueType]:
    async with session.get(url(f'/hero/{hero_id}/technique')) as res:
        return Response(res, HeroTechniqueType)


async def get_hero_technique(session, hero_id, technique_id) -> HeroTechniqueType | None:
    async with session.get(url(f'/hero/{hero_id}/technique/{technique_id}')) as res:
        if res.status == 200:
            return await res.json()

        return None


async def create_hero_technique(body, hero_id) -> HeroTechniqueType | None:
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/hero/{hero_id}/technique'), json=body)

        if res.status == 200:
            return await res.json()

        return None


async def delete_hero_technique(session, hero_id, technique_id) -> bool:
    async with session.get(url(f'/hero/{hero_id}/technique/{technique_id}')) as res:
        if res.status == 200:
            return True

        return False
