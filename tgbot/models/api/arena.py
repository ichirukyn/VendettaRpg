from typing import TypedDict

from tgbot.models.api.enemy_api import EnemyType


class ArenaEnemyType(TypedDict):
    id: int
    enemy_id: int
    floor_id: int
    team_id: int
    enemy: EnemyType


class ArenaType(TypedDict):
    id: int
    name: str
    desc: str
    chance_bonus: int
    max_rate_drop: int
