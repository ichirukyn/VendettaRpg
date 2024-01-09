from typing import TypedDict


class ClassType(TypedDict):
    id: int
    name: str
    desc: str
    desc_short: bool
    race_id: int
    main_attr: str


class ClassBonusType(TypedDict):
    id: int
    class_id: int
    name: str
    type: str
    attribute: str
    value: str
