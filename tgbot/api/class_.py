from tgbot.api._config import url
from tgbot.models.api.class_api import ClassBonusType
from tgbot.models.api.class_api import ClassType


async def get_class(session, class_id: int) -> ClassType | None:
    async with session.get(url(f'/class/{class_id}')) as res:
        if res.status == 200:
            return await res.json()

        return None


async def fetch_class(session, ) -> [ClassType]:
    async with session.get(url(f'/class')) as res:
        return await res.json()


async def fetch_class_bonuses(session, class_id: int) -> [ClassBonusType]:
    async with session.get(url(f'/class/{class_id}/effect')) as res:
        return await res.json()
