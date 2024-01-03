import requests

from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.class_api import ClassBonusType
from tgbot.models.api.class_api import ClassType


def get_class(class_id: int) -> Response[ClassType]:
    res = requests.get(url(f'/class/{class_id}'))
    return Response(res, ClassType)


def fetch_class() -> [ClassType]:
    res = requests.get(url(f'/class'))
    return res.json()


def fetch_class_bonuses(class_id: int) -> [ClassBonusType]:
    res = requests.get(url(f'/class/{class_id}/bonus'))
    return res.json()
