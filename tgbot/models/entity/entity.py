from random import randint
from random import random

from tgbot.models.entity.entity_base.entity_damage import EntityDamage
from tgbot.models.entity.entity_base.entity_level import EntityLevel
from tgbot.models.entity.entity_base.entity_resist import EntityResist
from tgbot.models.entity.entity_base.entity_weapon import EntityWeapon
from tgbot.models.entity.race import Race
from tgbot.models.entity.skill import Skill


class Entity(EntityResist, EntityDamage, EntityWeapon, EntityLevel, Race):
    lvl = 1
    team_id = 0
    is_leader = False

    mana = 1
    mana_max = 1
    mana_percent = 1  # 1 - 100%

    hp = 1
    hp_percent = 1  # 1 - 100%
    hp_max = 1

    # Deprecated
    technique_damage = 1
    # Deprecated
    technique_name = ''

    technique = None

    active_bonuses = []
    effects = []
    skills = []
    techniques = []
    select_skill = None
    race = None
    _class = None
    statistic = None

    action = ''
    sub_action = ''
    target = None

    mana_modify = 10
    hp_modify = 10

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
        self.hp_percent = 1
        self.mana_percent = 1

    def update_stats(self):
        self.mana = self.mana_max
        self.hp_max = self.health * self.hp_modify

        self.update_stats_percent()
        self.total_stats = self.sum_stats()

    def update_stats_all(self):
        self.mana = self.mana_max
        self.hp = self.health * self.hp_modify
        self.hp_max = self.health * self.hp_modify

        self.update_stats_percent()
        self.total_stats = self.sum_stats()

    def update_stats_percent(self):
        self.hp_percent = round(self.hp_max / self.hp)
        self.mana_percent = round(self.mana_max / self.mana)

    def sum_stats(self):
        return self.flat_strength + self.flat_health + self.flat_speed + self.flat_dexterity + self.flat_soul + \
            self.flat_intelligence + self.flat_submission

    def check_active_skill(self):
        for bonus in self.active_bonuses:
            if len(bonus.effects) == 0:
                self.active_bonuses.remove(bonus)

            if isinstance(bonus, Skill):
                bonus.turn_check()

    # def init_race_bonus(self, race_bonus: Race):
    #     self.race_bonus = race_bonus
    #     self.race_bonus.race_apply()

    def is_active_skill(self, name):
        for skill in self.active_bonuses:
            if skill.name == name:
                return True

        return False

    def debuff_control_check(self, action):
        check = True

        for debuff in self.debuff_list:
            if action == 'move' and debuff['type'] == 'stun':
                check = False
            if action == 'turn' and debuff['type'] == 'root':
                check = False

        return check

    def debuff_round_check(self):
        log = None
        for debuff in self.debuff_list:
            if debuff['duration'] <= 0:
                self.debuff_list.remove(debuff)
                log = f"{self.name} снял ослабление ({debuff.get('name')})"

            debuff['duration'] -= 1

            if debuff['type'] == 'period':
                log = self.period_damage(debuff)

        return log

    def technique_round_check(self):
        for tech in self.techniques:
            if len(tech.effects) == 0:
                self.techniques.remove(tech)

            tech.cooldown_decrease()

    def technique_target(self) -> str:
        direction = 'my'

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

        damage = main_attr * (1 + debuff['damage']) * (1 + element_damage)
        defs = (100 + attacker.lvl) / \
               ((100 + self.lvl) * (1 - def_res) * (1 - attacker.ignore_resist) + (100 + attacker.lvl))

        total_damage = round(damage * defs)

        self.prev_period = total_damage
        self.total_period += total_damage
        self.hp -= total_damage
        return f"{self.name} получил урон {debuff.get('name')} ({total_damage})"

    def effect_chance_check(self, base_chance, target) -> bool:
        chance = base_chance * (1 + self.effect_chance) * (1 - target.effect_resist) * (1 - target.debuff_resist)
        print('real_effect_probability', chance)

        if random() < chance:
            return True

        return False

    def damage(self, defender, damage_type) -> int:
        def_res = defender.__getattribute__(damage_type)
        dmg_attr = self.__getattribute__(self._class.main_attr)

        base_dmg = self.technique.damage * (dmg_attr + self.weapon_damage)
        bonus_type = self.__getattribute__(damage_type) + 1

        # TODO 1 - 0 -- Сопротивления элем. урону | 1 - 0 -- Игнорирование защиты
        defs = (100 + self.lvl) / ((100 + defender.lvl) * (1 - def_res) * (1 - self.ignore_resist) + (100 + self.lvl))

        total_damage = (base_dmg * bonus_type * self.bonus_damage * (defs + defender.resist)) + 1

        if defender.sub_action == 'Защита':
            defense = randint(5, 40) / 100

            # TODO 0 -- бонус экипировки
            total_damage_def = \
                (base_dmg * bonus_type * defense * self.bonus_damage * (defs * defender.resist + defense)) + 0
            total_damage = total_damage_def

            self.statistic.battle.block_damage += total_damage - total_damage_def

        if random() < self.crit_rate:
            total_damage = total_damage + (total_damage * self.crit_damage)
            self.statistic.battle.crit_count += 1

        if defender.sub_action == 'Контрудар':
            cs = round(total_damage * randint(10, 35) / 100)
            self.hp -= cs
            self.statistic.battle.counter_strike_count += 1

        evasion_chance = defender.speed / (defender.speed + self.speed)

        if self._class.type == 'Лучник':
            evasion_chance = defender.speed / (defender.speed + self.speed + (self.accuracy * 1.5))

        if defender.sub_action == 'Уворот' and random() < evasion_chance:
            self.statistic.battle.evasion_count += 1
            return 0

        return round(total_damage)
