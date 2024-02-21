from typing import List
from typing import TypedDict

from tgbot.models.api.effect_api import EffectType


class TechniqueType(TypedDict):
    id: int
    name: str
    desc: str
    desc_short: str
    damage: int
    type_damage: str
    distance: str
    is_stack: bool
    class_id: int
    race_id: int
    type: str
    cooldown: int
    effects: List[EffectType]


class CreateTechniqueType(TypedDict):
    name: str
    desc: str
    desc_short: str
    damage: int
    type_damage: str
    distance: str
    is_stack: bool
    class_id: int
    race_id: int
    type: str
    cooldown: int
