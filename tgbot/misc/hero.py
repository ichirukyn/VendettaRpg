from tgbot.api.hero import get_hero
from tgbot.api.hero import get_hero_lvl
from tgbot.api.hero import get_hero_stats
from tgbot.api.statistic import get_statistic
from tgbot.api.user import get_user_chat_id
from tgbot.models.entity._class import class_init
from tgbot.models.entity.hero import Hero
from tgbot.models.entity.hero import HeroFactory
from tgbot.models.entity.race import race_init
from tgbot.models.entity.skill import skills_init
from tgbot.models.entity.statistic import Statistic
from tgbot.models.entity.techniques import technique_init
from tgbot.models.user import DBCommands


async def init_hero(db: DBCommands, session, hero_id, is_full=True) -> Hero:
    hero_data = await get_hero(session, hero_id, 0)
    hero_db = await hero_data.json()

    stats_db = await get_hero_stats(session, hero_id)

    hero_lvl_data = await get_hero_lvl(session, hero_id)
    hero_lvl = await hero_lvl_data.json()

    chat_id: str = await get_user_chat_id(session, int(hero_db['user_id']))
    hero_db['chat_id'] = int(chat_id)

    hero: Hero = HeroFactory.create_hero(hero_id, hero_db, stats_db)
    hero.flat_init()
    hero.update_stats_all()
    hero.init_level(hero_lvl)

    if is_full:
        hero = await full_init_hero(db, session, hero_id, hero, hero_db)

    return hero


async def full_init_hero(db, session, hero_id, hero, hero_db):
    team_db = await db.get_hero_team(hero_id)
    statistic_data = await get_statistic(session, hero_id)
    statistic_db = await statistic_data.json()

    skills = await db.get_hero_skills(hero_id)

    hero_weapon = await db.get_hero_weapons(hero_id)
    weapon = await db.get_weapon(hero_weapon['weapon_id'])

    hero.active_bonuses = []
    hero = await race_init(session, hero, hero_db['race_id'])
    hero = await class_init(session, hero, hero_db['class_id'])

    hero.techniques = []
    technique_db = await db.get_hero_techniques(hero.id)

    hero.statistic = Statistic()
    hero.statistic.init_from_db(statistic_db)

    for tech in technique_db:
        technique_bonuses = await db.get_technique_bonuses(tech['technique_id'])
        hero = technique_init(hero, tech, technique_bonuses)

    if skills:
        hero = await skills_init(hero, skills, db)

    if hero_weapon:
        hero.add_weapon(weapon, hero_weapon['lvl'])

    if team_db is not None:
        hero.team_id = team_db['team_id']

        if team_db['is_leader']:
            hero.name = f' {hero.name}'
            hero.is_leader = True

    return hero


async def init_team(db, session, team, hero=None):
    entity_team = []

    for entity in team:
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
