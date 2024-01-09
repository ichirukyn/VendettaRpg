import aiohttp

from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.user_api import CreateUserType
from tgbot.models.api.user_api import UserType


async def create_user(body: CreateUserType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/user'), json=body)
        return await res.json()


async def get_user(session, chat_id: str) -> Response[UserType]:
    res = await session.get(url(f'/user/{chat_id}'))
    return Response(res, UserType)


async def get_user_chat_id(session, user_id: int) -> str:
    res = await session.get(url(f'/user/{user_id}/chat_id'))
    return await res.text()


async def fetch_user(session) -> [UserType]:
    res = await session.get(url(f'/user'))
    return await res.json()

# data = {
#     'chat_id': '792451145',
#     'login': 'Ichirus',
#     'is_admin': False,
#     'ref_id': 1,
# }
#
# print(create_user(data))
