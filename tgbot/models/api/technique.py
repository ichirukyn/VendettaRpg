from typing import TypedDict


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
