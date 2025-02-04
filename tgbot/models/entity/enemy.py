from random import choice
from random import randint

from tgbot.api.enemy import fetch_enemy_technique
from tgbot.api.enemy import get_enemy
from tgbot.enums.skill import SkillDirection
from tgbot.enums.skill import SkillSubAction
from tgbot.enums.skill import SkillType
from tgbot.handlers import lib_stats
from tgbot.misc.hero import entity_base_init
from tgbot.misc.locale import keyboard
from tgbot.models.entity.entity import Entity
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
    def auto_distribute(self, delta, tags=None):
        if self.lvl >= 3 or delta >= 5:
            delta += randint(-2, 3)

        # TODO: Заменить на ранг и подключить как-то начальную +20 (в конце)
        # points_to_add = (delta * 10 * (1 + (self.rank / 10))) + 20

        points_to_add = (delta * 10) + 20

        self.lvl += delta
        print('Ожидаемое кол-во: ', points_to_add, f'({(self.lvl * 10) + 20 + 8})\n')

        self.update_stats_all()

        if tags is not None:
            combined_priorities = {}

            # Слияние приоритетов из тегов с использованием lib_stats для соответствия ключей
            for tag in tags:
                for key in lib_stats:
                    k = lib_stats[key]
                    k_ = None

                    if key in ['Сила', 'Ловкость', 'Интеллект']:
                        k_ = self._class.main_attr

                    if k not in combined_priorities.keys():
                        combined_priorities[k] = 0

                    if k_ is not None and k_ not in combined_priorities.keys():
                        combined_priorities[k_] = 0

                    combined_priorities[k_ or k] += round(tag.get(k, 0) * tag.get('priority', 0), 2)

            # Нормализация приоритетов
            total_priority = sum(combined_priorities.values()) or 1
            print(f'Приоритеты: {combined_priorities}')

            normalized_priorities = {
                attr: priority / total_priority for attr, priority in combined_priorities.items()
            }

            normalized_priorities = self.adjust_priorities(normalized_priorities)

            print(f'Приоритеты норм: {normalized_priorities}\n')
            # Распределение свободных очков с учетом приоритетов
            for attr, priority in normalized_priorities.items():
                points_for_attr = round(points_to_add * priority)
                setattr(self, attr, getattr(self, attr) + points_for_attr)
        else:
            self.strength += (self.strength / self.total_stats) * points_to_add
            self.health += (self.health / self.total_stats) * points_to_add
            self.speed += (self.speed / self.total_stats) * points_to_add
            self.dexterity += (self.dexterity / self.total_stats) * points_to_add
            self.accuracy += (self.accuracy / self.total_stats) * points_to_add
            self.soul += (self.soul / self.total_stats) * points_to_add
            self.intelligence += (self.intelligence / self.total_stats) * points_to_add
            self.submission += (self.submission / self.total_stats) * points_to_add

        # TODO: Заменить на что-то более четкое..
        self.weapon_damage += delta * 3

        self.update_stats_all()
        print('Полученное кол-во: ', self.total_stats, '\n')

        return self

    def adjust_priorities(self, normalized_priorities):
        # Получаем текущие значения характеристик
        current_attributes = {attr: getattr(self, attr) for attr in normalized_priorities.keys()}
        total_attributes = sum(current_attributes.values())

        # Вычисляем текущее соотношение характеристик
        current_ratios = {attr: value / total_attributes for attr, value in current_attributes.items() if value > 0}

        # Вычисляем разницу между текущим соотношением и нормализованными приоритетами
        ratio_difference = {
            attr: current_ratios.get(attr, 0) - normalized_priorities.get(attr, 0) for attr in normalized_priorities
            if normalized_priorities[attr] > 0
        }

        # Корректируем нормализованные приоритеты на основе разницы
        for attr, difference in ratio_difference.items():
            if difference < 0:
                # Если текущее значение меньше желаемого, увеличиваем приоритет
                normalized_priorities[attr] += abs(difference)
            elif difference > 0:
                # Если текущее значение больше желаемого, уменьшаем приоритет
                normalized_priorities[attr] -= difference

        # Перенормализация приоритетов после корректировки
        total_priority = sum(normalized_priorities.values())
        adjusted_priorities = {
            attr: priority / total_priority for attr, priority in normalized_priorities.items() if priority > 0
        }

        return adjusted_priorities

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
            elif round(self.hp_percent) <= 0.1:
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

    technique_db = await fetch_enemy_technique(session, enemy_id)

    enemy = await entity_base_init(session, enemy_db, technique_db, enemy)

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

# strength: 0.2
# health: 0.2
# priority: 3
#
# strength: 0.25
# health: 0.15
# speed: 0.15
# priority: 4
