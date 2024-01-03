import json

import requests

from tgbot.api import url
from tgbot.models.api.api import Response
from tgbot.models.api.statistic import StatisticType


def create_statistic(body: StatisticType) -> StatisticType:
    res = requests.post(url(f'/statistic'), json=body)
    return res.json()


def update_statistic(body: StatisticType, hero_id: int) -> StatisticType:
    res = requests.put(url(f'/statistic/{hero_id}'), json=body)
    return res.json()


def get_statistic(hero_id: str) -> Response[StatisticType]:
    res = requests.get(url(f'/statistic/{hero_id}'))
    return Response(res, StatisticType)


def get_statistic_chat_id(statistic_id: int) -> str:
    res = requests.get(url(f'/statistic/{statistic_id}/chat_id'))
    return res.json()


def fetch_statistic() -> [StatisticType]:
    res = requests.get(url(f'/statistic'))
    return res.json()


def statistics_to_json(statistics):
    data = {
        'damage': statistics.damage,
        'damage_max': statistics.damage_max,
        'healing': statistics.healing,
        'healing_max': statistics.healing_max,
        'damage_taken': statistics.damage_taken,
        'damage_taken_max': statistics.damage_taken_max,
        'block_damage': statistics.block_damage,
        'counter_strike_damage': statistics.counter_strike_damage,
        'hits_count': statistics.hits_count,
        'miss_count': statistics.miss_count,
        'crit_count': statistics.crit_count,
        'money_all': statistics.money_all,
        'money_wasted': statistics.money_wasted,
        'evasion_count': statistics.evasion_count,
        'evasion_success_count': statistics.evasion_success_count,
        'block_count': statistics.block_count,
        'counter_strike_count': statistics.counter_strike_count,
        'pass_count': statistics.pass_count,
        'escape_count': statistics.escape_count,
        'win_one_to_one': statistics.win_one_to_one,
        'win_team_to_team': statistics.win_team_to_team,
        'lose_one_to_one': statistics.lose_one_to_one,
        'lose_team_to_team': statistics.lose_team_to_team,
        'kill_enemy': statistics.kill_enemy,
        'kill_hero': statistics.kill_hero,
        'death': statistics.death,
    }

    return data

# print(create_statistic(data))
