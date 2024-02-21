from typing import TypedDict


class UserType(TypedDict):
    id: int
    chat_id: str
    login: str
    is_admin: bool
    is_baned: bool
    ref_id: int


class CreateUserType(TypedDict):
    chat_id: str
    login: str
    ref_id: int
