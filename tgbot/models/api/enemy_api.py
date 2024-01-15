from typing import TypedDict


class EnemyType(TypedDict):
    id: int
    name: str
    race_id: int
    class_id: int
    rank: str


class EnemyStatsType(TypedDict):
    id: int
    enemy_id: int
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


class CreateEnemyType(TypedDict):
    id: int
    name: str
    race_id: int
    class_id: int


class EnemyTechniqueType(TypedDict):
    id: int
    enemy_id: int
    technique_id: int
    lvl: int
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


class CreateEnemyTechniqueType(TypedDict):
    id: int
    enemy_id: int
    technique_id: int
    lvl: int
