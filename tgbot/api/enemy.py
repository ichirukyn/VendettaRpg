from typing import List

import aiohttp

from tgbot.api import url
from tgbot.models.api.enemy_api import CreateEnemyType
from tgbot.models.api.enemy_api import EnemyItemType
from tgbot.models.api.enemy_api import EnemyStatsType
from tgbot.models.api.enemy_api import EnemyTechniqueType
from tgbot.models.api.enemy_api import EnemyType


async def create_enemy(body: CreateEnemyType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/enemy'), json=body)
        return await res.json()


async def get_enemy(session, enemy_id: int) -> EnemyType:
    async with session.get(url(f'/enemy/{enemy_id}')) as res:
        return await res.json()


async def fetch_enemy(session, ) -> [EnemyType]:
    async with session.get(url(f'/enemy')) as res:
        return await res.json()


# Stats
async def get_enemy_stats(session, enemy_id) -> [EnemyStatsType]:
    res = await session.get(url(f'/enemy/{enemy_id}/stats'))
    return await res.json()


# Technique
async def fetch_enemy_technique(session, enemy_id) -> List[EnemyTechniqueType] | None:
    async with session.get(url(f'/enemy/{enemy_id}/technique')) as res:
        if res.status == 200:
            return await res.json()
        return None


async def get_enemy_technique(session, enemy_id, technique_id) -> EnemyTechniqueType | None:
    async with session.get(url(f'/enemy/{enemy_id}/technique/{technique_id}')) as res:
        if res.status == 200:
            return await res.json()

        return None


async def create_enemy_technique(body, enemy_id) -> EnemyTechniqueType | None:
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/enemy/{enemy_id}/technique'), json=body)

        if res.status == 200:
            return await res.json()

        return None


async def delete_enemy_technique(session, enemy_id, technique_id) -> bool:
    async with session.get(url(f'/enemy/{enemy_id}/technique/{technique_id}')) as res:
        if res.status == 200:
            return True

        return False


# Technique
async def fetch_enemy_item(session, enemy_id) -> List[EnemyTechniqueType] | None:
    async with session.get(url(f'/enemy/{enemy_id}/technique')) as res:
        if res.status == 200:
            return await res.json()
        return None


async def get_enemy_loot(session, enemy_id, hero_id) -> List[EnemyItemType] | None:
    async with session.get(url(f'/enemy/{enemy_id}/loot'), params={'hero_id': hero_id}) as res:
        if res.status == 200:
            return await res.json()

        return None
