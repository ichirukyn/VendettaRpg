from typing import Optional
from typing import TypedDict

from tgbot.models.api.level_api import LevelType


class HeroType(TypedDict):
    id: int
    chat_id: Optional[str]
    user_id: int
    name: str
    clan: str
    race_id: int
    class_id: int
    rank: str
    money: int
    limit_os: int
    evolution: int


class HeroStatsType(TypedDict):
    id: int
    hero_id: int
    lvl: int
    strength: int
    health: int
    speed: int
    accuracy: int
    dexterity: int
    soul: int
    intelligence: int
    submission: int
    crit_rate: int
    crit_damage: int
    resist: int
    total_stats: int


class HeroLvlType(TypedDict):
    id: int
    hero_id: int
    lvl: int
    exp: int
    level: LevelType


class CreateHeroType(TypedDict):
    user_id: int
    name: str
    race_id: int
    class_id: int
