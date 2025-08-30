from random import randint
from random import random

from tgbot.enums.skill import SkillSubAction
from tgbot.misc.other import formatted
from tgbot.models.entity.entity_base.entity_aggression import EntityAggression
from tgbot.models.entity.entity_base.entity_damage import EntityDamage
from tgbot.models.entity.entity_base.entity_level import EntityLevel
from tgbot.models.entity.entity_base.entity_resist import EntityResist
from tgbot.models.entity.entity_base.entity_stats import EntityStats
from tgbot.models.entity.entity_base.entity_weapon import EntityWeapon
from tgbot.models.entity.spells import Spell
from tgbot.models.entity.statistic import Statistic, StatisticBattle
from tgbot.models.entity.techniques import Technique


class EntityFactory:
    @staticmethod
    def create_entity(user_id, name):
        entity = {
            'entity_id': user_id,
            'name': name,
            'rank': 'Редкий',
            'strength': 1,
            'health': 1,
            'speed': 1,
            'dexterity': 1,
            'accuracy': 1,
            'soul': 1,
            'intelligence': 1,
            'submission': 1,
            'crit_rate': 0.05,
            'crit_damage': 0.5,
            'resist': 0.1,
        }
        return Entity(**entity)


class Entity(EntityResist, EntityDamage, EntityWeapon, EntityLevel, EntityStats, EntityAggression):
    lvl = 1
    team_id = 0
    is_leader = False

    mana = 1
    mana_max = 1
    mana_reg = 0
    mana_percent = 1  # 1 - 100%

    qi = 1
    qi_max = 1
    qi_reg = 0
    qi_percent = 1  # 1 - 100%

    hp = 1
    hp_max = 1
    hp_percent = 1  # 1 - 100%
    hp_health_modify = 1

    shield = 0
    shield_max = 0
    shield_percent = 0  # 1 - 100%
    shield_modify = 1

    technique: Technique | None = None
    spell: Spell | None = None

    select_skill = None
    race = None
    _class = None
    statistic = None

    action = ''
    sub_action = ''
    target = None

    control_mana = 0
    control_mana_normalize = 0

    control_qi = 0
    control_qi_normalize = 0

    hp_modify = 1  # Мод. Хп
    qi_modify = 1  # Мод. Ки
    mana_modify = 1  # Мод. Маны

    flat_strength = 0
    flat_health = 0
    flat_speed = 0
    flat_dexterity = 0
    flat_accuracy = 0
    flat_soul = 0
    flat_intelligence = 0
    flat_submission = 0

    # Для эффектов
    prev = 0
    prev_percent = 0
    prev_period = 0
    total_period = 0

    evasion_modify = 0
    counter_modify = 0
    defence_modify = 0

    effect_resist = 0
    effect_chance = 0
    debuff_resist = 0  # https://honkai-star-rail.fandom.com/wiki/Abundance_Sprite:_Malefic_Ape

    bonus_damage = 1

    # Для модели
    class_id = 0
    race_id = 0

    is_enemy = False
    is_me = False
    turn = 0

    # TODO: Перенести всё в init
    def __init__(self, entity_id, name, rank, strength, health, speed, dexterity, accuracy, soul, intelligence,
                 submission, crit_rate, crit_damage, resist):
        self.id = entity_id

        self.name = name
        self.rank = rank

        self.strength = strength
        self.health = health
        self.speed = speed
        self.dexterity = dexterity
        self.accuracy = accuracy
        self.soul = soul
        self.intelligence = intelligence
        self.submission = submission

        self.crit_rate = crit_rate
        self.crit_damage = crit_damage
        self.resist = resist

        self.debuff_list = []

        self.total_stats_flat = self.sum_flat_stats()
        self.total_stats = self.sum_stats()

        self.active_bonuses = []
        self.effects = []
        self.spells = []
        self.techniques = []

        self.potion = None
        self.potions = []
        self.potion_cd = 0

        self.postfix = ""

    # Stats
    def flat_init(self):
        self.flat_strength = self.strength
        self.flat_health = self.health
        self.flat_speed = self.speed
        self.flat_dexterity = self.dexterity
        self.flat_accuracy = self.accuracy
        self.flat_soul = self.soul
        self.flat_intelligence = self.intelligence
        self.flat_submission = self.submission

    def default_stats(self):
        self.mana = self.mana_max
        self.hp = self.hp_max
        self.qi = self.qi_max

        self.hp_percent = 1
        self.qi_percent = 1
        self.mana_percent = 1

        self.update_control()

    def update_regen(self):
        self.qi_reg = ((self.strength / 2) + self.health) / 3
        self.mana_reg = ((self.intelligence / 2) + self.soul) / 3

        if self.dexterity > self.strength:
            self.qi_reg = ((self.dexterity / 2) + self.health) / 3

    def update_stats(self):
        self.hp_max = round(self.health) * self.hp_modify
        self.mana_max = round(self.soul) * self.mana_modify

        if self.flat_strength >= self.flat_dexterity:
            self.qi_max = round(self.health) * self.qi_modify
        else:
            self.qi_max = (round(self.health) + (0.25 * round(self.dexterity))) * self.qi_modify

        self.update_control()
        self.update_stats_percent()
        self.total_stats_flat = self.sum_flat_stats()

    def update_control(self):
        self.control_mana = (2 * self.intelligence * self.soul) / (self.intelligence + self.soul)
        self.control_mana_normalize = self.control_mana / max(self.intelligence, self.soul)

        if self.flat_strength >= self.flat_dexterity:
            self.control_qi = (2 * self.strength * self.health) / (self.strength + self.health)
            self.control_qi_normalize = self.control_qi / max(self.strength, self.health)
        else:
            self.control_qi = (2 * self.dexterity * self.health) / (self.dexterity + self.health)
            self.control_qi_normalize = self.control_qi / max(self.dexterity, self.health)

    def update_stats_all(self):
        self.hp_max = round(self.health) * self.hp_modify
        self.mana_max = round(self.soul) * self.mana_modify

        self.hp = round(self.health) * self.hp_modify
        self.mana = round(self.soul) * self.mana_modify

        if self.flat_strength >= self.flat_dexterity:
            self.qi = round(self.health) * self.qi_modify
            self.qi_max = round(self.health) * self.qi_modify
        else:
            self.qi = (round(self.health) + (0.25 * round(self.dexterity))) * self.qi_modify
            self.qi_max = (round(self.health) + (0.25 * round(self.dexterity))) * self.qi_modify

        if self.shield <= 0:
            self.shield = 0

        self.update_control()
        self.update_stats_percent()
        self.total_stats_flat = self.sum_flat_stats()
        self.total_stats = self.sum_stats()

    def update_stats_percent(self):
        self.hp_percent = 0 if self.hp_percent <= 0 else round((self.hp * 100) / self.hp_max)
        self.mana_percent = 0 if self.mana_percent <= 0 else round((self.mana * 100) / self.mana_max)
        self.qi_percent = 0 if self.qi_percent <= 0 else round((self.qi * 100) / self.qi_max)
        self.shield_percent = 0 if self.shield_percent <= 0 else round((self.shield * 100) / self.shield_max)

    def sum_flat_stats(self):
        return self.flat_strength + self.flat_health + self.flat_speed + self.flat_dexterity + self.flat_soul + \
            self.flat_intelligence + self.flat_submission + self.flat_accuracy

    def sum_stats(self):
        return self.strength + self.health + self.speed + self.dexterity + self.soul + self.intelligence + \
            self.submission + self.accuracy

    def turn_regenerate(self):
        self.update_regen()
        self.qi += self.qi_reg
        self.mana += self.mana_reg

        if self.qi > self.qi_max:
            self.qi = self.qi_max

        if self.mana > self.mana_max:
            self.mana = self.mana_max

        self.update_stats_percent()

    def check_shield(self):
        if self.shield > self.shield_max:
            self.shield_max = self.shield

    # Battle
    def default_aggression(self):
        self.aggression = (self.aggression_base + self.total_stats) * self.aggression_mod

    def check_active_effects(self):
        active_bonuses = [*self.active_bonuses]

        if not hasattr(active_bonuses, '__iter__') or len(self.active_bonuses) < 1:
            return print('Не хочет итерироваться..', self.active_bonuses)

        for bonus in active_bonuses:
            if len(bonus.effects) == 0:
                try:
                    self.active_bonuses.remove(bonus)
                except ValueError as e:
                    print(e)
                    print('test')

            if isinstance(bonus, Technique) or isinstance(bonus, Spell):
                if bonus.cooldown_current <= 0 and bonus.cooldown != 0:
                    bonus.deactivate(self)

                    if bonus in self.active_bonuses:
                        self.active_bonuses.remove(bonus)

                bonus.cooldown_decrease()
                bonus.check_effect(self)

    def skill_cooldown(self):
        if len(self.techniques) > 0:
            for technique in self.techniques:
                technique.cooldown_decrease()

        if len(self.spells) > 0:
            for spell in self.spells:
                spell.cooldown_decrease()

        if self.potion_cd > 0:
            self.potion_cd -= 1

    def is_active_skill(self, name):
        for skill in self.active_bonuses:
            if skill.name == name:
                return True

        return False

    def debuff_control_check(self, action):
        check = True

        for debuff in self.debuff_list:
            if action == 'move' and debuff.get('attribute') == 'stun':
                check = False
            if action == 'turn' and debuff.get('attribute') == 'root':
                check = False

        return check

    def debuff_round_check(self):
        log = ''
        for debuff in self.debuff_list:
            if debuff['duration'] <= 0:
                self.debuff_list.remove(debuff)
                return f"{self.name} снял ослабление ({debuff.get('name')})"

            debuff['duration'] -= 1

            if debuff['type'] == 'period':
                log += f"{self.period_damage(debuff)}\n"

        if log == '':
            log = None

        return log

    def technique_round_check(self):
        for tech in self.techniques:
            if len(tech.effects) == 0:
                self.techniques.remove(tech)

            tech.cooldown_decrease()

    def get_target(self) -> str:
        direction = 'my'
        action = self.technique

        if self.spell is not None:
            action = self.spell

        if action is None:
            return direction

        for bonus in action.bonuses:
            if bonus.direction == 'my':
                continue

            elif bonus.direction != 'my':
                direction = bonus.direction

        if len(action.bonuses) == 0:
            direction = 'enemy'

        return direction

    def period_damage(self, debuff):
        attacker = debuff['target']

        if debuff['element']:
            element_damage = attacker.__getattribute__(debuff['element'])
        else:
            element_damage = 0

        main_attr = attacker.__getattribute__(attacker._class.main_attr)
        def_res = self.__getattribute__(debuff['element'])

        damage = main_attr * (1 + element_damage)
        defs = (100 + attacker.lvl) / \
               ((100 + self.lvl) * (1 - def_res) * (1 - attacker.ignore_resist) + (100 + attacker.lvl))

        total_damage = round(damage * defs)

        self.prev_period = total_damage
        self.total_period += total_damage
        self.hp -= total_damage
        return f"{self.name} получил урон {debuff.get('name')} ({total_damage})"

    def get_evasion(self, attacker):
        action = attacker.technique

        if attacker.spell is not None:
            action = attacker.spell

        level_difference = abs(self.lvl - attacker.lvl)

        if level_difference <= 5:
            scatter_coefficient = 1.0 + (level_difference * 0.05)
        else:
            scatter_coefficient = 1.0 + (level_difference * 0.1)

        evasion_chance = (self.speed / (self.speed + attacker.speed)) + self.evasion_modify
        evasion_chance *= scatter_coefficient

        if attacker._class.type == 'Лучник' or (hasattr(action, 'distance') and action.distance == 'distant'):
            evasion_chance = (self.speed / (self.speed + attacker.speed + (attacker.accuracy * 1.5)))
            evasion_chance += self.evasion_modify

        evasion_chance = max(0.05, min(evasion_chance, 0.95))

        return evasion_chance

    # TODO: На "Подумать"
    # def get_evasion(self, attacker):
    #     evasion_chance = (self.speed / (self.speed + attacker.speed)) + self.evasion_modify
    #
    #     # Используем линейную интерполяцию для модификатора точности
    #     # accuracy_modifier = (attacker.accuracy * 1.5) / ((attacker.accuracy * 1.5) + self.speed)
    #     # interpolated_accuracy_modifier = evasion_chance * (1 - accuracy_modifier) + 0.1 * accuracy_modifier
    #
    #     # evasion_chance_1 = interpolated_accuracy_modifier + self.evasion_modify
    #
    #     evasion_chance_1 = 0.5 * (evasion_chance + (1 - evasion_chance))
    #
    #     # level_difference = max(1, abs(self.lvl - attacker.lvl))
    #     # scatter_coefficient = 1 / level_difference
    #
    #     # Лучше
    #     # level_difference = self.lvl - attacker.lvl
    #     # scatter_coefficient = 1.0 + (level_difference * 0.1)
    #
    #     level_difference = abs(self.lvl - attacker.lvl)
    #
    #     if level_difference <= 5:
    #         scatter_coefficient = 1.0 + (level_difference * 0.05)
    #     else:
    #         scatter_coefficient = 1.0 + (level_difference * 0.1)
    #
    #     print(
    #         f"\n"
    #         f"{self.name}\n"
    #         f"Без точности:\n"
    #         f"Шанс уклонения обычный: {round(evasion_chance, 2) * 100}%\n"
    #         f"Шанс уклонения интерполяция: {round(evasion_chance_1, 2) * 100}%\n"
    #         f"Шанс уклонения уровни: {round(evasion_chance * scatter_coefficient, 2) * 100}%\n"
    #         f"Шанс уклонения уровни и интерполяция: {round(evasion_chance_1 * scatter_coefficient, 2) * 100}%\n"
    #         f"self - Скорость: {round(self.speed)}, Точность: {round(self.accuracy)}\n"
    #         f"attacker - Скорость: {round(attacker.speed)}, Точность: {round(attacker.accuracy)}\n"
    #         f"\n"
    #     )
    #
    #     action = attacker.technique
    #     if attacker.spell is not None:
    #         action = attacker.spell
    #
    #     if attacker._class.type == 'Лучник' or action.distance == 'distant':
    #         evasion_chance = (self.speed / (self.speed + attacker.speed + (attacker.accuracy * 1.5)))
    #         evasion_chance += self.evasion_modify
    #
    #     # # Используем линейную интерполяцию для модификатора точности
    #     # accuracy_modifier = (attacker.accuracy * 1.5) / ((attacker.accuracy * 1.5) + self.speed)
    #     # interpolated_accuracy_modifier = evasion_chance * (1 - accuracy_modifier) + 0.1 * accuracy_modifier
    #     #
    #     # evasion_chance_1 = interpolated_accuracy_modifier + self.evasion_modify
    #
    #     evasion_chance_1 = 0.5 * (evasion_chance + (1 - evasion_chance))
    #
    #     print(
    #         f"\n"
    #         f"{self.name}\n"
    #         f"С точностью:\n"
    #         f"Шанс уклонения обычный: {round(evasion_chance, 2) * 100}%\n"
    #         f"Шанс уклонения интерполяция: {round(evasion_chance_1, 2) * 100}%\n"
    #         f"Шанс уклонения уровни: {round(evasion_chance * scatter_coefficient, 2) * 100}%\n"
    #         f"Шанс уклонения уровни и интерполяция: {round(evasion_chance_1 * scatter_coefficient, 2) * 100}%\n"
    #         f"self - Скорость: {round(self.speed)}, Точность: {round(self.accuracy)}\n"
    #         f"attacker - Скорость: {round(attacker.speed)}, Точность: {round(attacker.accuracy)}\n"
    #         f"\n"
    #     )
    #
    #     evasion_chance = max(0.05, min(evasion_chance, 0.95))
    #
    #     return evasion_chance

    def check_evasion(self, attacker):
        evasion_chance = self.get_evasion(attacker)

        if self.sub_action == SkillSubAction.evasion and random() < evasion_chance:
            attacker.statistic.battle.evasion_count += 1
            return True

        return False

    def effect_chance_check(self, base_chance, target_adder) -> bool:
        evasion_chance = (target_adder.accuracy / ((target_adder.accuracy * 0.7) + self.speed)) + self.evasion_modify
        effect_chance = target_adder.effect_chance + evasion_chance
        chance = base_chance * (1 + effect_chance) * (1 - self.effect_resist) * (1 - self.debuff_resist)

        if random() < chance:
            return True

        return False

    def damage(self, defender, damage_type, technique=None):
        tech = self.technique
        log = ''
        is_crit = False

        if self.spell is not None:
            tech = self.spell

        if technique is not None:
            tech = technique

        if damage_type != 'none':
            bonus_type = 1 + self.__getattribute__(damage_type)
            def_res = defender.__getattribute__(damage_type.replace('damage', 'resist'))
        else:
            bonus_type = 1
            def_res = 0

        if tech.type_attack == 'all':
            dmg_attr = self.__getattribute__(self._class.main_attr)
        else:
            dmg_attr = self.__getattribute__(tech.type_attack or self._class.main_attr)

        base_dmg = tech.damage * (dmg_attr + self.weapon_damage)

        cof = 1.2

        defs = (100 + self.lvl) / ((100 + defender.lvl) * (1 - def_res) * (1 - defender.resist)
                                   * (1 + self.ignore_resist) + (100 + self.lvl) * (1 + cof))

        total_damage = (base_dmg * bonus_type * self.bonus_damage * (1 - defs)) + 0

        if random() < self.crit_rate:
            total_damage = total_damage + (total_damage * self.crit_damage)

            self.statistic.battle.crit_count += 1
            is_crit = True
            log = f' ⚡️'

        if defender.sub_action == SkillSubAction.defense:
            defense = (round(randint(7, 20)) / 100) + self.defence_modify

            total_damage_ = total_damage * (1 - defense)

            def_damage = round(total_damage - total_damage_)

            if def_damage > 0:
                self.statistic.battle.block_damage += def_damage
                log += f'\n🛡 {defender.name} заблокировал {def_damage} урона'

            total_damage = total_damage_

        if defender.sub_action == SkillSubAction.counter_strike:
            cs = round(total_damage * randint(10, 35) / 100) + self.counter_modify

            self.hp -= cs
            self.statistic.battle.counter_strike_count += 1
            log += f'\n🪃 {defender.name} контратаковал на {formatted(cs)} урона.'

        if round(total_damage) < 1:
            total_damage = 1

        if tech.damage == 0:
            return 0, None

        return round(total_damage), log

    def damage_demo(self, technique):
        entity = EntityFactory.create_entity(1, 'demo')
        entity.lvl = self.lvl

        # entity = copy.copy(self)
        self.base_resist(entity)

        entity.statistic = Statistic()
        entity.statistic.battle = StatisticBattle()

        entity.crit_rate = 0
        damage, _ = self.damage(entity, technique.type_damage, technique)

        return damage

    def base_resist(self, entity):
        entity.light_resist = 0.1
        entity.air_resist = 0.1
        entity.phys_resist = 0.1
        entity.dark_resist = 0.1
        entity.earth_resist = 0.1
        entity.fire_resist = 0.1
        entity.resist = 0.1
