import requests

from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.race_api import RaceBonusType
from tgbot.models.api.race_api import RaceType


def get_race(race_id: int) -> Response[RaceType]:
    res = requests.get(url(f'/race/{race_id}'))
    return Response(res, RaceType)


def fetch_race() -> [RaceType]:
    res = requests.get(url(f'/race'))
    return res.json()


def fetch_race_bonuses(race_id: int) -> [RaceBonusType]:
    res = requests.get(url(f'/race/{race_id}/bonus'))
    return res.json()
