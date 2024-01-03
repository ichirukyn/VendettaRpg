import requests

from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.hero_api import HeroLvlType
from tgbot.models.api.hero_api import HeroStatsType
from tgbot.models.api.hero_api import HeroType


def get_hero(hero_id: int, user_id: int | None) -> Response[HeroType]:
    res = requests.get(url(f'/hero/{str(hero_id)}'), params={'user_id': user_id})
    return Response(res, HeroType)


def get_hero_stats(hero_id) -> [HeroStatsType]:
    res = requests.get(url(f'/hero/{hero_id}/stats'))
    return res.json()


def get_hero_lvl(hero_id) -> Response[HeroLvlType]:
    res = requests.get(url(f'/hero/{hero_id}/lvl'))
    return Response(res, HeroLvlType)


def fetch_hero() -> [HeroType]:
    res = requests.get(url(f'/hero'))
    return res.json()
