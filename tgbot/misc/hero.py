from tgbot.models.entity.hero import Hero, HeroFactory
from tgbot.models.entity.skill import skills_init
from tgbot.models.user import DBCommands


async def init_hero(db: DBCommands, user_id) -> Hero:
    print('Hero init')

    hero_db = await db.get_heroes(user_id)
    stats_db = await db.get_hero_stats(hero_db['id'])

    team_db = await db.get_hero_team(user_id)

    race_db = await db.get_race(hero_db['race_id'])
    class_db = await db.get_class(hero_db['class_id'])

    skills = await db.get_hero_skills(hero_db['id'])
    hero_weapon = await db.get_hero_weapons(hero_db['id'])
    weapon = await db.get_weapon(hero_weapon['weapon_id'])

    hero: Hero = HeroFactory.create_hero(hero_db, stats_db, race_db, class_db)
    hero.update_stats_all()

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


async def init_team(db, team, hero=None):
    entity_team = []

    for entity in team:
        h = await init_hero(db, entity['hero_id'])

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


# TODO: Переписать потом, на инициализацию отдельных частей, а не всего hero
async def update_hero(db: DBCommands, hero) -> Hero:
    # print(f'Hero update - {hero.id} id')

    hero_db = await db.get_heroes(hero.id)
    stats_db = await db.get_hero_stats(hero.id)

    skills = await db.get_hero_skills(hero.id)
    hero_weapon = await db.get_hero_weapons(hero.id)

    team_db = await db.get_hero_team(hero.id)

    hero = await skills_init(hero, skills, db)

    # TODO: Костыль..
    hero.strength = stats_db['strength']
    hero.health = stats_db['health']
    hero.speed = stats_db['speed']
    hero.soul = stats_db['soul']
    hero.intelligence = stats_db['intelligence']
    hero.dexterity = stats_db['dexterity']
    hero.submission = stats_db['submission']
    hero.crit_rate = stats_db['crit_rate']
    hero.crit_damage = stats_db['crit_damage']
    hero.free_stats = stats_db['free_stats']
    hero.total_stats = stats_db['total_stats']
    hero.money = hero_db['money']

    hero.update_stats()

    if hero_weapon:
        weapon = await db.get_weapon(hero_weapon['weapon_id'])
        hero.add_weapon(hero_weapon, weapon)

    try:
        hero_team_bd = await db.get_hero_team(hero.id)
        hero.team_id = hero_team_bd['team_id']
    except TypeError:
        pass

    if team_db is not None:
        hero.team_id = team_db['team_id']

        if team_db['is_leader']:
            hero.name = f' {hero.name}'
            hero.is_leader = True

    return hero
