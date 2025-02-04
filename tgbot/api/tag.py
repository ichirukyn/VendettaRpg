import aiohttp

from tgbot.api._config import url
from tgbot.models.api.tag_api import CreateTagType
from tgbot.models.api.tag_api import TagType


async def create_tag(body: CreateTagType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/tag'), json=body)
        return await res.json()


async def get_tag(session, hero_id: int) -> TagType:
    async with session.get(url(f'/tag/{hero_id}')) as res:
        return await res.json()


async def fetch_tag(session, list_id) -> [TagType]:
    params = {'list_id': list_id}
    async with session.get(url(f'/tag'), params=params) as res:
        return await res.json()
