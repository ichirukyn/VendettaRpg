import asyncio

from tgbot.api.hero import fetch_hero_spell
from tgbot.api.hero import fetch_hero_technique
from tgbot.api.hero import get_hero
from tgbot.api.hero import get_hero_lvl
from tgbot.api.hero import get_hero_stats
from tgbot.api.statistic import get_statistic
from tgbot.misc.state import BattleState
from tgbot.models.entity._class import class_init
from tgbot.models.entity.hero import Hero
from tgbot.models.entity.hero import HeroFactory
from tgbot.models.entity.item import item_init
from tgbot.models.entity.race import race_init
from tgbot.models.entity.spells import spell_init
from tgbot.models.entity.statistic import Statistic
from tgbot.models.entity.techniques import technique_init
from tgbot.models.user import DBCommands

options_init = {
    'stats': True,
    'race': True,
    'class_': True,
    'statistic': True,
    'techniques': True,
    'spells': True,
    'weapon': True,
    'team': True,
}


async def init_hero(db: DBCommands, session, hero_id=None, chat_id=None, options=None) -> Hero:
    # start_time = time.perf_counter()  # Начало измерения времени

    if options is None:
        options = {**options_init}

    hero_db = None
    stats_db = None

    if hero_id is not None:
        hero_db, stats_db = await asyncio.gather(get_hero(session, hero_id), get_hero_stats(session, hero_id))

        chat_id_ = hero_db.get('user', {}).get('chat_id', '0')
        hero_db['chat_id'] = int(chat_id_)

    if chat_id is not None:
        hero_db['chat_id'] = chat_id

    hero = HeroFactory.create_hero(hero_id, hero_db, stats_db if options.get('stats') else {})

    if options.get('stats'):
        hero.flat_init()
        hero.active_bonuses = []
        _, hero = await check_hero_lvl(db, session, hero)

    if options.get('race'):
        race = await race_init(session, hero_db.get('race'))
        if race is not None:
            hero.race = race
            hero.race.apply(hero)

    if options.get('class_'):
        _class = await class_init(session, hero_db.get('class'))
        if _class is not None:
            hero._class = _class
            hero._class.apply(hero)

    if options.get('statistic'):
        statistic_db = await get_statistic(session, hero_id)
        hero.statistic = Statistic()
        hero.statistic.init_bd(statistic_db)

    if options.get('techniques'):
        techniques_db = await fetch_hero_technique(session, hero.id)
        hero.techniques = [technique_init(tech.get('technique')) for tech in techniques_db if tech.get('technique')]

    if options.get('spells'):
        spells_db = await fetch_hero_spell(session, hero.id)
        hero.spells = [spell_init(_spell.get('spell')) for _spell in spells_db if _spell.get('spell')]

    if options.get('weapon'):
        hero = await update_hero_weapon(db, hero)

    if options.get('team'):
        team_db = await db.get_hero_team(hero_id)

        if team_db is not None:
            hero.team_id = team_db.get('team_id')

            if team_db.get('is_leader'):
                hero.name = f' {hero.name}'
                hero.is_leader = True

    hero = await update_hero_potion(db, hero)
    hero.update_stats_all()

    # end_time = time.perf_counter()  # Конец измерения времени
    # duration = end_time - start_time  # Время выполнения

    return hero


async def entity_base_init(session, entity_db, technique_db, entity):
    _class = await class_init(session, entity_db.get('class'))
    if _class is not None:
        entity._class = _class
        entity._class.apply(entity)

    race = await race_init(session, entity_db.get('race'))
    if race is not None:
        entity.race = race
        entity.race.apply(entity)

    entity.techniques = []

    if technique_db is not None:
        for tech in technique_db:
            technique = tech.get('technique')
            technique = technique_init(technique)

            if technique is not None:
                entity.techniques.append(technique)

    return entity


async def check_hero_lvl(db, session, hero) -> (str, Hero):
    log: str = ''

    try:
        hero_lvl_data = await get_hero_lvl(session, hero.id)
        hero_lvl = await hero_lvl_data.json()
        hero.init_level(hero_lvl)

        if hero.check_lvl_up():
            hero.lvl += 1
            hero.free_stats += 10  # TODO: Тянуть с ранга

            log += f"\n\nВы достигли {hero.lvl} уровня!\nВы получили {10} СО"

            await db.update_hero_stat('free_stats', hero.free_stats, hero.id)
            await db.update_hero_level(hero.exp, hero.lvl, hero.id)

            log_, hero = await check_hero_lvl(db, session, hero)
            log += log_

    except Exception as e:
        print(f"An error occurred: {e}")

    return log, hero


async def update_hero_potion(db, hero):
    potions = await db.get_hero_inventory('potion', hero.id)

    for potion in potions:
        p = item_init(potion)
        hero.potions.append(p)

    return hero


async def update_hero_weapon(db, hero):
    hero_weapon = await db.get_hero_weapons(hero.id)
    weapon = await db.get_weapon(hero_weapon['weapon_id'])

    if hero_weapon:
        hero.init_weapon(weapon, hero_weapon['lvl'])

    return hero


async def init_team(db, session, team, dp, hero=None):
    entity_team = []

    for entity in team:
        user = await db.get_heroes(entity.get('hero_id'))
        chat_id = user.get('chat_id', 0)

        if chat_id != 0:
            state = await dp.storage.get_state(chat=chat_id)

            for s in BattleState.states:
                if state == s.state and state != 'BattleState:battle_start':
                    continue

        h = await init_hero(db, session, hero_id=entity['hero_id'])

        if len(entity['prefix']) > 0:
            prefix = f" \"{entity['prefix']}\""
            h.name += prefix

        if hero is not None and hero.id == entity['hero_id']:
            hero.name = h.name

        if entity['leader_id'] == h.id:
            h.is_leader = True
            h.name = f'👑 {h.name}'

        entity_team.append(h)

    return entity_team


def leader_on_team(team):
    for e in team:
        if e.is_leader:
            return e
