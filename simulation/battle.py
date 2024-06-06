import asyncio
import random
import re

import aiohttp

from simulation.source.logs import SimulationLogger
from tgbot.api.class_ import fetch_class
from tgbot.api.race import fetch_race
from tgbot.handlers.battle.interface import BattleFactory
from tgbot.keyboards.reply import home_kb
from tgbot.misc.state import LocationState
from tgbot.models.entity._class import class_init
from tgbot.models.entity.enemy import EnemyFactory
from tgbot.models.entity.race import race_init
from tgbot.models.entity.techniques import TechniqueFactory

# Конфиг logger
directory = './logs/battle'
file_pattern = 'battle_*.log'
log_name = 'battle'

logger = SimulationLogger(directory, file_pattern, log_name)


# Функция для логирования результатов действий
def log_action(entity, action_result):
    logger.logger.info(f"{entity.name}\n {action_result.get('log').strip()}")


avg_lvl = 5
battle_count = 5

pattern_team_key = r"team_\d+"

# TODO: Раса и класс не по id, а по порядку массива!!!! (Выровнял GET запросы, вроде по id, но лучше перепроверять)
team_config = [
    {'key': 'team_1', 'count': 1, 'race': 0, 'class': 1},
    {'key': 'team_2', 'count': 1, 'race': 1, 'class': 3},
]

base_technique_config = {
    'id': 1,
    'name': 'Удар',
    'desc': 'Удар',
    'damage': 0.5,
    'type_damage': 'none',
    'type_attack': 'all',
    'distance': 'melee',
    'is_stack': False,
    'type': 'attack',
    'cooldown': 0,
    'rank': 1,
}

base_technique = TechniqueFactory.create_technique(base_technique_config)


async def mobs_generate(session):
    teams = {'team_1': [], 'team_2': []}

    races = await fetch_race(session)
    classes = await fetch_class(session)

    for team in team_config:
        for i in range(0, team.get('count')):
            race_db = races[team.get('race')]

            if team.get('race') is None:
                race_db = random.choice(races)

            class_db = classes[team.get('class')]

            if team.get('race') is None:
                class_db = random.choice(classes)

            entity = EnemyFactory.create_enemy({})

            name = f"{race_db.get('name')} {class_db.get('name')} - {team.get('key')}__{i}"
            entity.name = name

            entity.flat_init()
            entity.auto_distribute(avg_lvl)

            race = await race_init(session, race_db)

            if race is not None:
                entity.race = race
                entity.race.apply(entity)

            _class = await class_init(session, class_db)

            if _class is not None:
                entity._class = _class
                entity._class.apply(entity)

            entity.techniques.append(base_technique)

            entity.update_stats_all()
            teams[team.get('key')].append(entity)

    return teams.get('team_1'), teams.get('team_2')


async def battle_wrapper():
    teams_score = {'team_1': 0, 'team_2': 0}

    for i in range(0, battle_count):
        session = aiohttp.ClientSession()

        team_1, team_2 = await mobs_generate(session)

        await session.close()

        engine_data = {
            "enemy_team": team_1,
            "player_team": team_2,
            "exit_state": LocationState.home,
            "exit_message": 'Была ошибка...\n',
            "exit_kb": home_kb,
            "battle_type": 'battle',
            "is_inline": False,
        }

        factory = BattleFactory(is_dev=True, **engine_data)

        engine = factory.create_battle_engine()
        engine.initialize()

        engine.battle()
        team_win = battle_simulation(engine)
        teams_score[team_win] += 1

    logger.logger.info(f'\n Счёт: {teams_score}')


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
        log_action(entity, action_result)  # Логирование действия

        entity.spell = None
        entity.technique = None

        if action_result is None:
            print('Ошибка action_result..')
            continue

        engine.save_entity(action_result['attacker'])

        if action_result['target'] is not None:
            engine.save_entity(action_result['target'], action_result['attacker'])


asyncio.run(battle_wrapper())
