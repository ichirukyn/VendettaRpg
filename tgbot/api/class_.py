from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.class_api import ClassBonusType
from tgbot.models.api.class_api import ClassType


async def get_class(session, class_id: int) -> Response[ClassType]:
    res = await session.get(url(f'/class/{class_id}'))
    return Response(res, ClassType)


async def fetch_class(session, ) -> [ClassType]:
    res = await session.get(url(f'/class'))
    return await res.json()


async def fetch_class_bonuses(session, class_id: int) -> [ClassBonusType]:
    res = await session.get(url(f'/class/{class_id}/effect'))
    return await res.json()
