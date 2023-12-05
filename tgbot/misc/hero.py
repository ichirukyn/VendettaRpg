from tgbot.models.entity._class import class_init
from tgbot.models.entity.hero import Hero
from tgbot.models.entity.hero import HeroFactory
from tgbot.models.entity.race import race_init
from tgbot.models.entity.skill import skills_init
from tgbot.models.user import DBCommands


async def init_hero(db: DBCommands, user_id=None, hero_id=None, is_full=True) -> Hero:
    if user_id is not None:
        hero_id = await db.get_hero_id(user_id)

    hero_db = await db.get_heroes(hero_id)

    stats_db = await db.get_hero_stats(hero_id)
    hero_lvl = await db.get_hero_lvl(hero_id)

    hero: Hero = HeroFactory.create_hero(hero_id, hero_db, stats_db)
    hero.flat_init()
    hero.update_stats_all()
    hero.init_level(hero_lvl)

    if is_full:
        await full_init_hero(db, hero_id, hero, hero_db)

    return hero


async def full_init_hero(db, hero_id, hero, hero_db):
    team_db = await db.get_hero_team(hero_id)

    skills = await db.get_hero_skills(hero_id)

    hero_weapon = await db.get_hero_weapons(hero_id)
    weapon = await db.get_weapon(hero_weapon['weapon_id'])

    hero = await race_init(hero, hero_db['race_id'], db)
    hero = await class_init(hero, hero_db['class_id'], db)

    if skills:
        hero = await skills_init(hero, skills, db)

    if hero_weapon:
        hero.add_weapon(weapon, hero_weapon['lvl'])

    if team_db is not None:
        hero.team_id = team_db['team_id']

        if team_db['is_leader']:
            hero.name = f' {hero.name}'
            hero.is_leader = True


async def init_team(db, team, hero=None):
    entity_team = []

    for entity in team:
        h = await init_hero(db, hero_id=entity['hero_id'])

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
