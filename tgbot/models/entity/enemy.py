from random import choice
from random import randint

from tgbot.api.enemy import fetch_enemy_technique
from tgbot.api.enemy import get_enemy
from tgbot.enums.skill import SkillDirection
from tgbot.enums.skill import SkillSubAction
from tgbot.enums.skill import SkillType
from tgbot.misc.locale import keyboard
from tgbot.models.entity._class import class_init
from tgbot.models.entity.entity import Entity
from tgbot.models.entity.race import race_init
from tgbot.models.entity.techniques import technique_init
from tgbot.models.user import DBCommands


class EnemyFactory:
    @staticmethod
    def create_enemy(data):
        enemy = {
            'entity_id': data.get('id', 0),
            'name': data.get('name', 'Enemy'),
            'rank': data.get('rank', 1),
            'strength': data.get('strength', 1) or 1,
            'health': data.get('health', 1) or 1,
            'speed': data.get('speed', 1) or 1,
            'dexterity': data.get('dexterity', 1) or 1,
            'accuracy': data.get('accuracy', 1) or 1,
            'soul': data.get('soul', 1) or 1,
            'intelligence': data.get('intelligence', 1) or 1,
            'submission': data.get('submission', 1) or 1,
            'crit_rate': data.get('crit_rate', 0.05),
            'crit_damage': data.get('crit_damage', 0.5),
            'resist': data.get('resist', 0),
        }

        return Enemy(**enemy)


class Enemy(Entity):
    def auto_distribute(self, delta):
        if self.lvl >= 3:
            delta += randint(-2, 3)

        # TODO: Заменить на ранг
        points_to_add = delta * 10
        self.lvl += delta

        self.update_stats_all()

        self.strength += (self.strength / self.total_stats) * points_to_add
        self.health += (self.health / self.total_stats) * points_to_add
        self.speed += (self.speed / self.total_stats) * points_to_add
        self.dexterity += (self.dexterity / self.total_stats) * points_to_add
        self.accuracy += (self.accuracy / self.total_stats) * points_to_add
        self.soul += (self.soul / self.total_stats) * points_to_add
        self.intelligence += (self.intelligence / self.total_stats) * points_to_add
        self.submission += (self.submission / self.total_stats) * points_to_add

        print('weapon_damage', self.weapon_damage)
        # TODO: Заменить на что-то более четкое..
        self.weapon_damage += delta * 5
        print('weapon_damage', self.weapon_damage)

        self.update_stats_all()

        return self

    def select_enemy(self, enemy_team):
        if len(enemy_team) > 0:
            self.target = max(enemy_team, key=lambda x: x.aggression)
        else:
            self.target = enemy_team[0]

    def select_target(self, teammates, enemies):
        target = self.get_target()

        if target == SkillDirection.my and self.technique.type == SkillType.support:
            self.target = self

        elif target == SkillDirection.enemy:
            self.select_enemy(enemies)

        elif target == SkillDirection.enemies:
            self.target = enemies

        elif target == SkillDirection.teammate:
            self.select_enemy(teammates)

        elif target == SkillDirection.teammates:
            self.target = teammates

        elif target == SkillDirection.enemy or self.technique.type == SkillType.attack:
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
        if len(self.active_bonuses) == 2 and len(self.spells) != 0:
            self.select_skill = choice(self.spells)
            self.action = keyboard['spell_list']
        else:
            self.action = keyboard['technique_list']

    def define_sub_action(self, team):
        if len(team) >= 1:
            entity = team[0]

            if entity.crit_rate > 0.4:
                return SkillSubAction.counter_strike
            elif self.speed > entity.speed:
                return SkillSubAction.evasion
            elif round(self.hp_percent) <= 2:
                return SkillSubAction.escape
            else:
                return SkillSubAction.defense
        elif len(team) > 1:
            faster = max(team, key=lambda x: x.speed)

            if self.speed > faster.speed:
                return SkillSubAction.evasion
            else:
                return SkillSubAction.defense
        else:
            return SkillSubAction.defense

async def init_enemy(db: DBCommands, enemy_id, session) -> Enemy:
    enemy_db = await get_enemy(session, enemy_id)
    stats_db = await db.get_enemy_stats(enemy_id)

    enemy_weapon = await db.get_enemy_weapon(enemy_id)
    weapon = await db.get_weapon(enemy_weapon.get('weapon_id', 1))

    enemy = EnemyFactory.create_enemy(stats_db)
    enemy.flat_init()
    # Костыль, чтобы противники могли больше спамить заклинаниями..
    enemy.qi_modify = 100
    enemy.mana_modify = 100

    enemy.lvl = stats_db['lvl']

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
