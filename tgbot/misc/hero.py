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
from tgbot.models.entity.race import race_init
from tgbot.models.entity.spells import spell_init
from tgbot.models.entity.statistic import Statistic
from tgbot.models.entity.techniques import technique_init
from tgbot.models.user import DBCommands


async def init_hero(db: DBCommands, session, hero_id=None, hero_data=None, chat_id=None) -> Hero:
    if hero_id is not None and hero_data is None:
        hero_db = await get_hero(session, hero_id)
        stats_db = await get_hero_stats(session, hero_id)

        _chat_id: str = hero_db.get('user').get('chat_id', '0')
        hero_db['chat_id'] = int(_chat_id)
    else:
        hero_id = hero_data['id']
        hero_db = hero_data
        hero_db['chat_id'] = hero_data.get('user').get('chat_id')
        stats_db = await get_hero_stats(session, hero_id)

    if chat_id is not None:
        hero_db['chat_id'] = chat_id

    hero: Hero = HeroFactory.create_hero(hero_id, hero_db, stats_db)
    hero.flat_init()
    hero.active_bonuses = []

    _, hero = await check_hero_lvl(db, session, hero)

    team_db = await db.get_hero_team(hero_id)
    statistic_db = await get_statistic(session, hero_id)


    _class = await class_init(session, hero_db.get('class'))

    if _class is not None:
        hero._class = _class
        hero._class.apply(hero)

    race = await race_init(session, hero_db.get('race'))

    if race is not None:
        hero.race = race
        hero.race.apply(hero)

    hero.statistic = Statistic()
    hero.statistic.init_bd(statistic_db)

    # Technique
    hero.techniques = []
    techniques_db = await fetch_hero_technique(session, hero.id)

    if techniques_db is not None:
        for tech in techniques_db:
            technique = tech.get('technique')
            technique = technique_init(technique)

            if technique is not None:
                hero.techniques.append(technique)

    # Spell
    hero.spells = []
    spells_db = await fetch_hero_spell(session, hero.id)

    if spells_db is not None:
        for _spell in spells_db:
            spell = _spell.get('spell')
            spell = spell_init(spell)

            if spell is not None:
                hero.spells.append(spell)

    hero = await update_hero_weapon(db, hero)

    if team_db is not None:
        hero.team_id = team_db['team_id']

        if team_db['is_leader']:
            hero.name = f' {hero.name}'
            hero.is_leader = True

    hero.update_stats_all()

    return hero


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


async def update_hero_stats(session, hero):
    stats_db = await get_hero_stats(session, hero.id)

    hero.init_stats_factory(stats_db)
    hero.flat_init()
    # Обновить бонусы
    hero.update_stats_all()

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
