from typing import Optional
from typing import TypedDict


class ItemType(TypedDict):
    id: int
    name: str
    desc: str
    value: int
    type: str
    modify: Optional[int]
    class_type: Optional[str]
    class_id: Optional[int]
    race_id: Optional[int]
