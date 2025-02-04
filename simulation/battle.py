import asyncio
import json
import logging
import os
import re
from pickle import dump
from pickle import load
from time import time

import aiohttp

from simulation.fetch import fetch
from simulation.generate import mobs_generate
from simulation.source.logs import SimulationLogger
from sql import create_pool
from tgbot.api.hero import get_hero
from tgbot.config import load_config
from tgbot.handlers.battle.interface import BattleFactory
from tgbot.keyboards.reply import home_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.state import LocationState
from tgbot.models.user import DBCommands

# from model.model import get_snapshot
# from model.model import predict_win

# Конфиг logger
directory = './logs/battle'
file_pattern = 'battle_*.log'
log_name = 'battle'

logger = SimulationLogger(directory, file_pattern, log_name, logging.DEBUG)

# TODO: Раса и класс не по id, а по порядку массива!!!! (Выровнял GET запросы, вроде по id, но лучше перепроверять)
pattern_team_key = r"team_\d+"

avg_lvl = 50
battle_count = 50

# {'key': 'team_1', 'count': 1, 'race': 0, 'class': 1, 'neuro': True, },
# {'key': 'team_2', 'count': 1, 'race': 1, 'class': 4, 'neuro': False, },


team_config = [
    {'key': 'team_1', 'count': 1, 'race': None, 'class': None, 'neuro': True, },
    {'key': 'team_2', 'count': 1, 'race': None, 'class': None, 'neuro': False, },
]

# True -- Если нужно обновить battle.json и results.json
is_collect_data = False


def save_data(filename, data):
    if not is_collect_data:
        return

    if os.path.getsize(filename) <= 0:
        dump([], open(filename, 'wb'))

    old_data = load(open(filename, 'rb')) or []
    dump([*old_data, data], open(filename, 'wb'))


async def battle_1_vs_1(races, classes, techniques, teams_score, result_vector, team_config, win_callback):
    for i in range(0, battle_count):
        print(f'Бой - {i}:\n')
        turn_vector = []

        session = aiohttp.ClientSession()

        team_1, team_2 = await mobs_generate(session, races, classes, techniques, team_config, avg_lvl)

        await session.close()

        engine_data = {
            "enemy_team": team_1,
            "player_team": team_2,
            "exit_state": LocationState.home,
            "exit_message": 'Была ошибка...\n',
            "exit_kb": home_kb,
            "battle_type": 'battle',
            "is_inline": False,
            # "callback": lambda teams: get_snapshot(teams, turn_vector)
        }

        factory = BattleFactory(**engine_data)

        engine = factory.create_battle_engine()
        engine.initialize()

        engine.battle()
        team_win = battle_simulation(engine)
        # print(team_win[0].name)

        teams_score[team_win] += 1

        win_callback(team_win)

        if 'team_1' == team_win:
            result_vector.append(1)
            # predict_win([engine.player_team, engine.enemy_team], turn_vector, 1)
        else:
            result_vector.append(0)
            # predict_win([engine.player_team, engine.enemy_team], turn_vector, 0)

        save_data('data/battle.pkl', turn_vector)


def win_score(team_win, score):
    if 'team_1' == team_win:
        score['win'] += 1
    else:
        score['loose'] += 1


async def battle_class_win_rate(races, classes, techniques, teams_score, result_vector):
    all_win_rate = []

    # x -- Первый класс, который сражается с каждым y классом, n количество раз
    for x in range(0, len(classes)):
        win_rate = {'name': f"{classes[x].get('name')} ({classes[x].get('id')})", 'battles': [], "rate": 0}

        for y in range(0, len(classes)):
            if classes[x].get('id') == classes[y].get('id'):
                continue

            score = {'name': f"{classes[y].get('name')} ({classes[y].get('id')})", 'win': 0, 'loose': 0}

            team_config = [
                {'key': 'team_1', 'count': 1, 'race': classes[x].get('race_id'), 'class': classes[x].get('id'),
                 'neuro': True, },
                {'key': 'team_2', 'count': 1, 'race': classes[x].get('race_id'), 'class': classes[y].get('id'),
                 'neuro': False, },
            ]

            await battle_1_vs_1(races, classes, techniques, teams_score, result_vector, team_config,
                                lambda x: win_score(x, score))

            win_rate['battles'].append(score)

        all_win_rate.append(win_rate)

    for win in all_win_rate:
        print(win.get('name'))

        wins = 0
        looses = 0

        for battle in win.get('battles'):
            print(battle, '\n')

            wins += battle.get('win', 0)
            looses += battle.get('loose', 0)

        rate = wins / (wins + looses)

        win['rate'] = round(rate, 2)

        print(f"Винрейт: {round(rate, 2)} ({wins}, {looses}) \n\n\n")

    all_win_rate.sort(key=lambda x: x.get('rate'))

    json.dump(all_win_rate, open('data/win_rate.json', 'w', encoding='utf-8'), ensure_ascii=False)


async def battle_wrapper():
    teams_score = {'team_1': 0, 'team_2': 0}
    result_vector = []

    races, classes, techniques = await fetch()

    # Начальное время
    start_time = time()

    # Основной код:
    await battle_class_win_rate(races, classes, techniques, teams_score, result_vector)

    # Конечное время
    end_time = time()

    # разница между конечным и начальным временем
    elapsed_time = end_time - start_time
    print('Время: ', round(elapsed_time, 3))

    save_data('data/results.pkl', result_vector)
    logger.logger.info(f'\nСчёт: {teams_score}')


def battle_simulation(engine):
    while True:
        order, entity, who, i, log = engine.battle()

        if who == 'win':
            team_win = engine.check_hp()
            team_win_name = re.search(pattern_team_key, team_win[0].name)

            if team_win_name:
                logger.logger.info(f"\nПобедитель: {team_win_name.group()}")
                return team_win_name.group()

        action_result = engine.battle_action(entity, entity.target)
        logger.logger.debug(f"{action_result.get('log').strip()}\n")

        entity.spell = None
        entity.technique = None

        if action_result is None:
            print('Ошибка action_result..')
            continue

        engine.save_entity(action_result['attacker'])

        if action_result['target'] is not None:
            engine.save_entity(action_result['target'], action_result['attacker'])


async def get_db():
    try:
        config = load_config("../.env")
        db = await create_pool(config)
        return DBCommands(db)
    except RuntimeError as e:
        # logger.logger.error(e)
        return None


async def predict_me_win(me, enemy):
    ids = [me, enemy]

    db = await get_db()

    if db is None:
        return

    teams = []

    for id in ids:
        session = aiohttp.ClientSession()

        hero_data = await get_hero(session, int(id))
        hero = await init_hero(db, session, hero_data.get('id'), hero_data.get('chat_id', None))

        if id == me:
            hero.is_me = True

        teams.append([hero])

        await session.close()

    # predict_win(teams, [])


if __name__ == '__main__':
    asyncio.run(battle_wrapper())
    # for _ in range(3):
    #     asyncio.run(predict_me_win(35, 10))
    # try:
    # except Exception as e:
    #     logger.logger.info(f"Error:\n{e}")
