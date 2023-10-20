from random import choice

from tgbot.models.entity.entity import Entity
from tgbot.models.entity.skill import skills_init
from tgbot.models.user import DBCommands


class EnemyFactory:
    @staticmethod
    def create_enemy(data, race, _class):
        enemy = {
            'entity_id': data['id'],
            'name': data['name'],
            'rank': data['rank'],
            'strength': data['strength'],
            'health': data['health'],
            'speed': data['speed'],
            'dexterity': data['dexterity'],
            'soul': data['soul'],
            'intelligence': data['intelligence'],
            'submission': data['submission'],
            'crit_rate': data['crit_rate'],
            'crit_damage': data['crit_damage'],
            'resist': data['resist'],
            'race_id': race['id'],
            'class_id': _class['id'],
            'race_name': race['name'],
            'class_name': _class['name'],
        }

        return Enemy(**enemy)


class Enemy(Entity):
    # def __init__(self, entity_id, name, rank, money, strength, health, speed, dexterity, soul, intelligence, submission,
    #              crit_rate, crit_damage, resist):
    #     super().__init__(entity_id, name, rank, money, strength, health, speed, dexterity, soul, intelligence,
    #                      submission, crit_rate, crit_damage, resist)

    def select_target(self, team):
        if len(team) > 0:
            self.target = min(team, key=lambda x: x.hp)
        else:
            self.target = team[0]

    def define_action(self):
        if len(self.active_bonuses) == 0 and len(self.skills) != 0:
            self.select_skill = choice(self.skills)
            self.action = 'Навыки'
        else:
            self.action = 'Атака'

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


async def init_enemy(db: DBCommands, enemy_id) -> Enemy:
    print('Enemy init')

    stats_db = await db.get_enemy_stats(enemy_id)
    skills = await db.get_enemy_skills(enemy_id)

    enemy_weapon = await db.get_enemy_weapon(enemy_id)
    weapon = await db.get_weapon(enemy_weapon['weapon_id'])

    race_db = await db.get_race(stats_db['race_id'])
    class_db = await db.get_class(stats_db['class_id'])

    enemy = EnemyFactory.create_enemy(stats_db, race_db, class_db)
    enemy = await skills_init(enemy, skills, db)
    enemy.add_weapon(weapon, enemy_weapon['lvl'])
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
