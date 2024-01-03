import requests

from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.user_api import UserType, CreateUserType


def create_user(body: CreateUserType) -> UserType:
    print(body)
    res = requests.post(url(f'/user'), data=body)
    return res.json()


def get_user(chat_id: str) -> Response[UserType]:
    res = requests.get(url(f'/user/{chat_id}'))
    return Response(res, UserType)


def get_user_chat_id(user_id: int) -> str:
    res = requests.get(url(f'/user/{user_id}/chat_id'))
    return res.json()


def fetch_user() -> [UserType]:
    res = requests.get(url(f'/user'))
    return res.json()

# data = {
#     'chat_id': '792451145',
#     'login': 'Ichirus',
#     'is_admin': False,
#     'ref_id': 1,
# }
#
# print(create_user(data))
