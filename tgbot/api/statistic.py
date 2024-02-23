from tgbot.api._config import url
from tgbot.models.api.statistic import StatisticType


async def create_statistic(session, body: StatisticType) -> StatisticType:
    res = await session.post(url(f'/statistic'), json=body)
    return await res.json()


async def update_statistic(session, body: StatisticType, hero_id: int) -> StatisticType:
    async with session.put(url(f'/statistic/{hero_id}'), json=body) as res:
        return await res.json()


async def get_statistic(session, hero_id: str) -> StatisticType | None:
    async with session.get(url(f'/statistic/{hero_id}')) as res:
        if res.status == 200:
            return await res.json()

        return None


async def fetch_statistic(session, ) -> [StatisticType]:
    async with session.get(url(f'/statistic')) as res:
        return await res.json()


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
        'count_one_to_one': statistics.count_one_to_one,
        'count_team_to_team': statistics.count_team_to_team,
        'kill_enemy': statistics.kill_enemy,
        'kill_hero': statistics.kill_hero,
        'death': statistics.death,
    }

    return data
