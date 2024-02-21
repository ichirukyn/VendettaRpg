from typing import TypedDict


class RaceType(TypedDict):
    id: int
    name: str
    desc: str
    desc_short: bool


class RaceBonusType(TypedDict):
    id: int
    race_id: int
    name: str
    type: str
    attribute: str
    value: str
