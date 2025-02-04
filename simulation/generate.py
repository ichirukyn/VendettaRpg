from random import choice

from simulation import base_technique
from tgbot.api.enemy import fetch_enemy_technique
from tgbot.api.tag import fetch_tag
from tgbot.api.technique import fetch_technique
from tgbot.models.entity._class import class_init
from tgbot.models.entity.enemy import EnemyFactory, Enemy
from tgbot.models.entity.hero import HeroInfo
from tgbot.models.entity.race import race_init
from tgbot.models.entity.statistic import StatisticBattle, Statistic
from tgbot.models.entity.techniques import technique_init


async def base_init(session, entity, race_db, class_db):
    race = await race_init(session, race_db)

    if race is not None:
        entity.race = race
        entity.race_id = race.id

    _class = await class_init(session, class_db)

    if _class is not None:
        entity._class = _class
        entity.class_id = _class.id


async def mob_generate(team, races, classes, techniques, session, avg_lvl=1) -> Enemy:
    # Base entity
    entity = EnemyFactory.create_enemy({})
    entity.flat_init()
    entity.rank = team.get('rank', 1)
    entity.id = team.get('id', 0)

    # Race
    race_db = choice(races)

    if team.get('race') is not None:
        # race_db = races[team.get('race') - 1]
        race_db = [race for race in races if race.get('id', 1) == team.get('race')][0]

    # Class
    class_db = choice(classes)

    if team.get('class') is not None:
        # class_db = classes[team.get('class') - 1]
        class_db = [class_ for class_ in classes if class_.get('id', 1) == team.get('class')][0]

    # Technique
    if len(techniques) > 1:
        for technique in techniques:
            if technique.get('class_id') == entity.class_id:
                tech = technique_init(technique)

                if tech is not None:
                    entity.techniques.append(tech)

    else:
        technique_db = await fetch_technique(session, race_db.get('id'), class_db.get('id'))

        if team.get('id'):
            technique_db_ = await fetch_enemy_technique(session, team.get('id'))
            techniques_ = []

            for tech in technique_db_:
                t = tech.get('technique')

                if t is not None:
                    is_unic = True

                    for x in technique_db:
                        if t.get('id') == x.get('id'):
                            is_unic = False

                    if is_unic:
                        techniques_.append(t)

            # Убираем дубликаты "удар" "сгусток" и прочего такого
            is_flat = False
            for t in technique_db:
                if t.get('damage') == 0.5 and t.get('cooldown') == 0 and t.get('type_attack') == 'all':
                    if is_flat:
                        print('Найдено:', t)
                        technique_db.remove(t)
                    else:
                        is_flat = True

            technique_db = [*technique_db, *techniques_]
            print(technique_db)

        if technique_db is not None:
            for tech in technique_db:
                technique = technique_init(tech)

                if technique is not None:
                    entity.techniques.append(technique)

    await base_init(session, entity, race_db, class_db)

    list_tag_id = [entity.race.tag_id, entity._class.tag_id]

    tags = [class_db.get('tag', []), race_db.get('tag', [])]

    if class_db.get('tag', None) is None or race_db.get('tag', None) is None:
        tags = await fetch_tag(session, list_tag_id)

    entity.lvl = 0
    entity.auto_distribute(avg_lvl, tags)

    # Бонусы
    entity.race.apply(entity)
    entity._class.apply(entity)

    # Base technique
    entity.techniques.append(base_technique)

    name = f"{race_db.get('name')} {class_db.get('name')} - {team.get('key')}"
    entity.name = team.get('name', name)

    # Костыли..
    entity.qi_modify += 2
    entity.mana_modify += 2
    entity.hp_modify += 1

    entity.update_stats_all()

    entity.statistic = Statistic()
    entity.statistic.battle = StatisticBattle()

    print(f"{entity.name} ({entity.race.name}, {entity._class.name})")
    print(HeroInfo().status(entity))
    print("\n\n")

    return entity
    # logger.logger.info(f'\n{entity.name}\n{HeroInfo.status_stats(entity)}\n\n\n')


async def mobs_generate(session, races, classes, techniques, team_config, avg_lvl):
    teams = {'team_1': [], 'team_2': []}

    for team in team_config:
        for i in range(0, team.get('count')):
            entity = await mob_generate(team, races, classes, techniques, session, avg_lvl)
            teams[team.get('key')].append(entity)

        if team.get('neuro'):
            choice(teams[team.get('key')]).is_me = True

    return teams.get('team_1'), teams.get('team_2')
