from typing import TypedDict


class TagType(TypedDict):
    id: int
    name: str
    desc: str
    priority: int
    strength: int
    health: int
    speed: int
    accuracy: int
    dexterity: int
    soul: int
    intelligence: int
    submission: int


class CreateTagType(TypedDict):
    name: str
    user_id: int
    race_id: int
    class_id: int
