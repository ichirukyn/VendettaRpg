from typing import TypedDict


class EffectType(TypedDict):
    id: int
    technique_id: int
    name: str
    type: str
    attribute: str
    value: int
    condition_attr: str
    condition: str
    condition_val: str
    direction: str
    duration: int
    is_single: bool
