from tgbot.api._config import url
from tgbot.models.api.arena import ArenaEnemyType
from tgbot.models.api.arena import ArenaType


async def get_arena(session, floor_id: int) -> ArenaType | None:
    async with session.get(url(f'/arena/{floor_id}')) as res:
        if res.status == 200:
            return await res.json()

        return None


async def fetch_arena(session) -> [ArenaType]:
    async with session.get(url(f'/arena')) as res:
        return await res.json()


async def fetch_arena_enemies(session, floor_id: int) -> [ArenaEnemyType]:
    async with session.get(url(f'/arena/{floor_id}/enemy')) as res:
        return await res.json() or []


async def get_arena_enemy(session, floor_id, enemy_id) -> ArenaEnemyType | None:
    async with session.get(url(f'/arena/{floor_id}/enemy/{enemy_id}')) as res:
        return await res.json()
