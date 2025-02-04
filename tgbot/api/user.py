import aiohttp

from tgbot.api._config import url
from tgbot.models.api.user_api import CreateUserType
from tgbot.models.api.user_api import UserType


async def create_user(body: CreateUserType):
    async with aiohttp.ClientSession() as session:
        res = await session.post(url(f'/user'), json=body)
        print("Create USER: ", body)
        return await res.json()


async def get_user(session, chat_id: str) -> UserType | None:
    async with session.get(url(f'/user/{chat_id}')) as res:
        if res.status == 200:
            return await res.json()
        return None


async def get_user_chat_id(session, user_id: int) -> str:
    async with session.get(url(f'/user/{user_id}/chat_id')) as res:
        return await res.text()


async def get_user_hero(session, user_id: int) -> UserType | None:
    async with session.get(url(f'/user/{user_id}/hero')) as res:
        if res.status == 200:
            return await res.json()
        return None


async def fetch_user(session) -> [UserType]:
    async with session.get(url(f'/user')) as res:
        return await res.json()

# data = {
#     'chat_id': '792451145',
#     'login': 'Ichirus',
#     'is_admin': False,
#     'ref_id': 1,
# }
