from random import choice

from tgbot.api.enemy import fetch_enemy_technique
from tgbot.api.enemy import get_enemy
from tgbot.misc.locale import keyboard
from tgbot.models.entity._class import class_init
from tgbot.models.entity.entity import Entity
from tgbot.models.entity.race import race_init
from tgbot.models.entity.skill import skills_init
from tgbot.models.entity.techniques import technique_init
from tgbot.models.user import DBCommands


class EnemyFactory:
    @staticmethod
    def create_enemy(data):
        enemy = {
            'entity_id': data['id'],
            'name': data['name'],
            'rank': data['rank'],
            'strength': data['strength'],
            'health': data['health'],
            'speed': data['speed'],
            'dexterity': data['dexterity'],
            'accuracy': data['accuracy'],
            'soul': data['soul'],
            'intelligence': data['intelligence'],
            'submission': data['submission'],
            'crit_rate': data['crit_rate'],
            'crit_damage': data['crit_damage'],
            'resist': data['resist'],
        }

        return Enemy(**enemy)


class Enemy(Entity):
    def __init__(self, entity_id, name, rank, strength, health, speed, dexterity, accuracy, soul, intelligence,
                 submission, crit_rate, crit_damage, resist):
        super().__init__(entity_id, name, rank, strength, health, speed, dexterity, accuracy, soul, intelligence,
                         submission, crit_rate, crit_damage, resist)
        self.techniques = []

    def select_enemy(self, enemy_team):
        if len(enemy_team) > 0:
            self.target = min(enemy_team, key=lambda x: x.hp)
        else:
            self.target = enemy_team[0]

    def select_target(self, teammates, enemies):
        target = self.technique_target()

        if target == 'my' and self.technique.damage == 0:
            self.target = self

        elif target == 'enemy':
            self.select_enemy(enemies)

        elif target == 'enemies':
            self.target = enemies

        elif target == 'teammate':
            self.select_enemy(teammates)

        elif target == 'teammates':
            self.target = teammates

        elif target == 'enemy' or self.technique.damage != 0:
            self.select_enemy(enemies)

    def choice_technique(self):
        check_list = []

        for tech in self.techniques:
            root_tech_check = tech.distance != 'distant' or tech.type == 'support'

            if not self.debuff_control_check('turn') and not root_tech_check:
                continue

            if tech.check(self):
                check_list.append(tech)

        if len(check_list) == 0:
            self.action = 'Пас'
            return False

        tech = choice(check_list)
        self.technique = tech
        return True

    def define_action(self):
        # TODO: Расширить проверку и отдельно вывести переменную для сложных нпс (== 4, а не 0, например)
        if len(self.active_bonuses) == 2 and len(self.skills) != 0:
            self.select_skill = choice(self.skills)
            self.action = keyboard['spell_list']
        else:
            self.action = keyboard['technique_list']

    def define_sub_action(self, team):
        if len(team) > 1:
            hp_percent = self.hp * self.hp_max / 100
            entity = team[0]

            if entity.crit_rate > 0.4:
                return 'Контрудар'
            elif self.speed > entity.speed:
                return 'Уклонение'
            elif round(hp_percent) < 2:
                return 'Сбежать'
            else:
                return 'Защита'
        else:
            faster = max(team, key=lambda x: x.speed)

            if self.speed > faster.speed:
                return 'Уклонение'
            else:
                return 'Защита'


async def init_enemy(db: DBCommands, enemy_id, session) -> Enemy:
    enemy_db = await get_enemy(session, enemy_id)
    stats_db = await db.get_enemy_stats(enemy_id)
    skills = await db.get_enemy_skills(enemy_id)

    enemy_weapon = await db.get_enemy_weapon(enemy_id)
    weapon = await db.get_weapon(enemy_weapon.get('weapon_id', 1))

    enemy = EnemyFactory.create_enemy(stats_db)
    enemy.lvl = stats_db['lvl']

    enemy = await skills_init(enemy, skills, db)
    enemy.init_weapon(weapon, enemy_weapon['lvl'])

    enemy.techniques = []
    technique_db = await fetch_enemy_technique(session, enemy_id)

    if technique_db is not None:
        for tech in technique_db:
            technique = tech.get('technique')
            technique = technique_init(technique)

            if technique is not None:
                enemy.techniques.append(technique)

    _class = await class_init(session, enemy_db.get('class'))
    if _class is not None:
        enemy._class = _class
        enemy._class.apply(enemy)

    race = await race_init(session, enemy_db.get('race'))
    if race is not None:
        enemy.race = race
        enemy.race.apply(enemy)

    enemy.update_stats_all()
    return enemy


# TODO: когда захочу добавить больше стратегий, вот заготовка..
class AggressiveEnemy(Enemy):
    # Определение действия во время хода
    def define_action(self):
        return 'attack'

    # Выбор подходящего дополнительного действия
    def define_sub_action(self, entity):
        return 'counterattack'


class DefensiveEnemy(Enemy):
    # Определение действия во время хода
    def define_action(self):
        if self.hp < self.hp_max * 0.5:
            return 'defense'
        else:
            return 'dodge'

    # Выбор подходящего дополнительного действия
    def define_sub_action(self, entity):
        if self.hp < self.hp_max * 0.5:
            return 'defense'
        else:
            return 'dodge'
