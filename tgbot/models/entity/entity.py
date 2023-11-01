from random import randint, random

from tgbot.models.entity.entity_base.entity_damage import EntityDamage
from tgbot.models.entity.entity_base.entity_level import EntityLevel
from tgbot.models.entity.entity_base.entity_resist import EntityResist
from tgbot.models.entity.entity_base.entity_weapon import EntityWeapon
from tgbot.models.entity.race import Race
from tgbot.models.entity.skill import SkillFactory, Skill


class Entity(EntityResist, EntityDamage, EntityWeapon, EntityLevel, Race):
    lvl = 1
    team_id = 0
    is_leader = False

    mana = 0
    mana_max = 0
    hp = 0
    hp_max = 0

    technique_damage = 1
    technique_name = ''

    # TODO: Заменить на что-то другое
    durability = 100
    durability_max = 100

    active_bonuses = []
    effects = []
    skills = []
    select_skill = None
    race = None

    action = ''
    sub_action = ''
    target = None

    mana_modify = 10
    hp_modify = 10

    flat_strength = 0
    flat_health = 0
    flat_speed = 0
    flat_dexterity = 0
    flat_soul = 0
    flat_intelligence = 0
    flat_submission = 0

    def __init__(self, entity_id, name, rank, strength, health, speed, dexterity, soul, intelligence, submission,
                 crit_rate, crit_damage, resist, class_id, class_name, main_attr):

        self.id = entity_id

        self.name = name
        self.rank = rank

        self.class_name = class_name
        self.class_id = class_id
        self.main_attr = main_attr

        self.strength = strength
        self.health = health
        self.speed = speed
        self.dexterity = dexterity
        self.soul = soul
        self.intelligence = intelligence
        self.submission = submission

        self.crit_rate = crit_rate
        self.crit_damage = crit_damage
        self.resist = resist

        self.total_stats = self.sum_stats()

    # Stats
    def flat_init(self):
        self.flat_strength = self.strength
        self.flat_health = self.health
        self.flat_speed = self.speed
        self.flat_dexterity = self.dexterity
        self.flat_soul = self.soul
        self.flat_intelligence = self.intelligence
        self.flat_submission = self.submission

    def default_stats(self):
        self.mana = self.mana_max
        self.hp = self.hp_max

    def update_stats(self):
        self.mana = self.mana_max
        self.hp_max = self.health * self.hp_modify

        self.total_stats = self.sum_stats()

    def update_stats_all(self):
        self.mana = self.mana_max
        self.hp = self.health * self.hp_modify
        self.hp_max = self.health * self.hp_modify

        self.total_stats = self.sum_stats()

    def sum_stats(self):
        return self.flat_strength + self.flat_health + self.flat_speed + self.flat_dexterity + self.flat_soul + \
            self.flat_intelligence + self.flat_submission

    def check_active_skill(self):
        for bonus in self.active_bonuses:
            if isinstance(bonus, Skill):
                bonus.skill_check()

    def init_skills(self, skills):
        for skill in skills:
            self.skills.append(SkillFactory.create_skill(self, skill))

    # def init_race_bonus(self, race_bonus: Race):
    #     self.race_bonus = race_bonus
    #     self.race_bonus.race_apply()

    def is_active_skill(self, name):
        for skill in self.active_bonuses:
            if skill.name == name:
                return True

        return False

    def damage(self, defender, damage_type):
        def_res = defender.__getattribute__(damage_type)
        dmg_attr = self.__getattribute__(self.main_attr)

        # TODO: Заменить Силу на основную характеристику класса
        base_dmg = self.technique_damage * (dmg_attr + self.weapon_damage)
        bonus_dmg = self.__getattribute__(damage_type) + 1

        # TODO 1 - 0 -- Сопротивления элем. урону | 1 - 0 -- Игнорирование защиты
        defs = (100 + self.lvl) / ((100 + defender.lvl) * (1 - def_res) * (1 - self.ignore_resist) + (100 + self.lvl))

        total_damage = (base_dmg * bonus_dmg * (defs + defender.resist)) + 1

        if defender.sub_action == 'Защита':
            print('Защита!')
            defense = randint(5, 40) / 100
            # TODO 0 -- бонус экипировки
            total_damage = (base_dmg * bonus_dmg * defense * (defender.resist + defense)) + 0
            defender.durability += 5

        if random() < self.crit_rate:
            print('Крит!')
            total_damage = total_damage + (total_damage * self.crit_damage)

        if defender.sub_action == 'Контрудар':
            cs = round(total_damage * randint(10, 35) / 100)
            self.hp -= cs

        evasion_chance = defender.speed / (defender.speed + self.speed)

        if defender.sub_action == 'Уворот' and random() < evasion_chance:
            print('Уклонение!')
            return 0

        return round(total_damage)
