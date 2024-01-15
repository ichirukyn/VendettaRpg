from typing import Optional
from typing import TypedDict

from tgbot.models.api.level_api import LevelType
from tgbot.models.api.technique import TechniqueType
from tgbot.models.api.user_api import UserType


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
    user: UserType


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
    name: str
    user_id: int
    race_id: int
    class_id: int


class HeroTechniqueType(TypedDict):
    id: int
    hero_id: int
    technique_id: int
    lvl: int
    technique: TechniqueType


class CreateHeroTechniqueType(TypedDict):
    id: int
    hero_id: int
    technique_id: int
    lvl: int
