from typing import TypedDict


class StatisticType(TypedDict):
    hero_id: int
    damage: int
    damage_max: int
    healing: int
    healing_max: int
    damage_taken: int
    damage_taken_max: int
    block_damage: int
    counter_strike_damage: int
    hits_count: int
    miss_count: int
    crit_count: int
    money_all: int
    money_wasted: int
    evasion_count: int
    evasion_success_count: int
    block_count: int
    counter_strike_count: int
    pass_count: int
    escape_count: int
    win_one_to_one: int
    win_team_to_team: int
    lose_one_to_one: int
    lose_team_to_team: int
    count_one_to_one: int
    count_team_to_team: int
    kill_enemy: int
    kill_hero: int
    death: int
