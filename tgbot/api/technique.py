import aiohttp

from tgbot.api._config import url
from tgbot.models.api.technique import CreateTechniqueType
from tgbot.models.api.technique import TechniqueType


async def create_technique(body: CreateTechniqueType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/technique'), json=body)
        return await res.json()


async def get_technique(session, technique_id: int) -> TechniqueType:
    async with session.get(url(f'/technique/{technique_id}')) as res:
        return await res.json()


async def fetch_technique(session, race_id, class_id) -> [TechniqueType]:
    async with session.get(url(f'/technique'), params={'class_id': class_id, 'race_id': race_id}) as res:
        return await res.json()


async def fetch_techniques(session) -> [TechniqueType]:
    async with session.get(url(f'/technique')) as res:
        return await res.json()
