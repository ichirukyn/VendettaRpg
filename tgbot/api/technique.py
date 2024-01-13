import aiohttp

from tgbot.api import url
from tgbot.models.api.technique import CreateTechniqueType
from tgbot.models.api.technique import TechniqueType


async def create_technique(body: CreateTechniqueType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/technique'), json=body)
        return await res.json()


async def get_technique(session, technique_id: int) -> TechniqueType:
    async with session.get(url(f'/technique/{technique_id}')) as res:
        return await res.json()


async def fetch_technique(session) -> [TechniqueType]:
    res = await session.get(url(f'/technique'))
    return await res.json()
