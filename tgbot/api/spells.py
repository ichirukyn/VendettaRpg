import aiohttp

from tgbot.api._config import url
from tgbot.models.api.spell import CreateSpellType
from tgbot.models.api.spell import SpellType


async def create_spell(body: CreateSpellType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/spell'), json=body)
        return await res.json()


async def get_spell(session, spell_id: int) -> SpellType:
    async with session.get(url(f'/spell/{spell_id}')) as res:
        return await res.json()


async def fetch_spell(session) -> [SpellType]:
    async with session.get(url(f'/spell')) as res:
        return await res.json()
