from random import randint
from random import random

from tgbot.misc.other import formatted
from tgbot.models.entity.entity_base.entity_damage import EntityDamage
from tgbot.models.entity.entity_base.entity_level import EntityLevel
from tgbot.models.entity.entity_base.entity_resist import EntityResist
from tgbot.models.entity.entity_base.entity_stats import EntityStats
from tgbot.models.entity.entity_base.entity_weapon import EntityWeapon
from tgbot.models.entity.skill import Skill
from tgbot.models.entity.techniques import Technique


class Entity(EntityResist, EntityDamage, EntityWeapon, EntityLevel, EntityStats):
    lvl = 1
    team_id = 0
    is_leader = False

    mana = 1
    mana_max = 1
    mana_percent = 1  # 1 - 100%

    qi = 1
    qi_max = 1
    qi_percent = 1  # 1 - 100%

    hp = 1
    hp_max = 1
    hp_percent = 1  # 1 - 100%

    shield = 0
    shield_max = 0
    shield_percent = 0  # 1 - 100%

    technique: Technique | None = None

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

    hp_modify = 0  # Мод. Хп
    qi_modify = 0  # Мод. Ки
    mana_modify = 0  # Мод. Маны

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

        self.total_stats = self.sum_stats()

        self.active_bonuses = []
        self.effects = []
        self.skills = []
        self.techniques = []

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

    def update_stats(self):
        self.hp_max = round(self.health) * self.hp_modify
        self.mana_max = round(self.soul) * self.mana_modify

        if self.flat_strength >= self.flat_dexterity:
            self.qi_max = round(self.health) * self.qi_modify
        else:
            self.qi_max = (round(self.health) + (0.25 * round(self.dexterity))) * self.qi_modify

        self.update_control()
        self.update_stats_percent()
        self.total_stats = self.sum_stats()

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
        self.total_stats = self.sum_stats()

    def update_stats_percent(self):
        if self.hp <= 0:
            self.hp_percent = 0
        else:
            self.hp_percent = round(self.hp_max / self.hp)

        if self.mana <= 0:
            self.mana_percent = 0
        else:
            self.mana_percent = round(self.mana_max / self.mana)

        if self.qi <= 0:
            self.qi_percent = 0
        else:
            self.qi_percent = round(self.qi_max / self.qi)

        if self.shield <= 0:
            self.shield_percent = 0
        else:
            self.shield_percent = round(self.shield_max / self.shield)

    def sum_stats(self):
        return self.flat_strength + self.flat_health + self.flat_speed + self.flat_dexterity + self.flat_soul + \
            self.flat_intelligence + self.flat_submission + self.flat_accuracy

    def turn_regenerate(self):
        self.qi += self.qi_max * 0.1
        self.mana += self.mana_max * 0.1

        if self.qi > self.qi_max:
            self.qi = self.qi_max

        if self.mana > self.mana_max:
            self.mana = self.mana_max

        self.update_stats_percent()

    def check_active_skill(self):
        for bonus in self.active_bonuses:
            if len(bonus.effects) == 0:
                self.active_bonuses.remove(bonus)

            if isinstance(bonus, Skill):
                bonus.turn_check(self)

            if isinstance(bonus, Technique):
                if bonus.cooldown_current <= 0 and bonus.cooldown != 0:
                    bonus.deactivate(self)

                    if bonus in self.active_bonuses:
                        self.active_bonuses.remove(bonus)

                if bonus not in self.techniques:
                    bonus.cooldown_decrease()
                    bonus.check_effect(self)

    def technique_cooldown(self):
        for technique in self.techniques:
            technique.cooldown_decrease()

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

    def technique_target(self) -> str:
        direction = 'my'

        if self.technique is None:
            return direction

        for bonus in self.technique.bonuses:
            if bonus.direction == 'my':
                continue

            elif bonus.direction != 'my':
                direction = bonus.direction

        if len(self.technique.bonuses) == 0:
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

    def check_evasion(self, attacker):
        evasion_chance = (self.speed / (self.speed + attacker.speed)) + self.evasion_modify
        # evasion_chance = (100 + self.lvl) / ((100 + defender.lvl) * (100 + defender.speed)
        # + (100 + defender.dexterity) + (100 + self.lvl))

        if attacker._class.type == 'Лучник' or attacker.technique.distance == 'distant':
            evasion_chance = (self.speed / (self.speed + attacker.speed + (attacker.accuracy * 1.5)))
            evasion_chance += self.evasion_modify

        if evasion_chance < 0.05:
            evasion_chance = 0.05

        if evasion_chance > 0.95:
            evasion_chance = 0.95

        print(
            f'Шанс уклонения {self.name} = {formatted(evasion_chance * 100)}% '
            f'(Скорость {formatted(self.speed)} vs {formatted(attacker.speed)}) '
            f'(Точность {formatted(attacker.accuracy)})\n'
        )

        if self.sub_action == 'Уворот' and random() < evasion_chance:
            attacker.statistic.battle.evasion_count += 1
            return True

        return False

    def effect_chance_check(self, base_chance, target) -> bool:
        chance = base_chance * (1 + self.effect_chance) * (1 - target.effect_resist) * (1 - target.debuff_resist)
        print('real_effect_probability', chance)

        if random() < chance:
            return True

        return False

    def damage(self, defender, damage_type) -> int:
        if damage_type != 'none':
            bonus_type = 1 + self.__getattribute__(damage_type)
            def_res = defender.__getattribute__(damage_type)
        else:
            def_res = 0
            bonus_type = 1

        dmg_attr = self.__getattribute__(self.technique.type_attack or self._class.main_attr)

        base_dmg = self.technique.damage * (dmg_attr + self.weapon_damage)

        # TODO 1 - 0 -- Сопротивления элем. урону | 1 - 0 -- Игнорирование защиты
        defs = (100 + self.lvl) / ((100 + defender.lvl) * (1 - def_res) * (1 - self.ignore_resist) + (100 + self.lvl))

        total_damage = (base_dmg * bonus_type * self.bonus_damage * (1 - (defs + defender.resist))) + 1

        if defender.sub_action == 'Защита':
            defense = round(randint(5, 15) / 100) + self.defence_modify

            # TODO 0 -- бонус экипировки
            total_damage_ = (base_dmg * bonus_type * self.bonus_damage * (1 - (defs + defender.resist + defense))) + 1
            total_damage = total_damage_

            self.statistic.battle.block_damage += round(total_damage - total_damage_)

        if random() < self.crit_rate:
            total_damage = total_damage + (total_damage * self.crit_damage)
            self.statistic.battle.crit_count += 1

        if defender.sub_action == 'Контрудар':
            cs = round(total_damage * randint(10, 35) / 100) + self.counter_modify
            self.hp -= cs
            self.statistic.battle.counter_strike_count += 1

        if round(total_damage) < 1:
            total_damage = 1

        return round(total_damage)
