from pony.orm import *

db = Database(provider='postgres', user='vendetta', password='vendetta', host='localhost', database='vendetta')


class User(db.Entity):
    _table_ = 'users'
    id = PrimaryKey(int, auto=True)
    chat_id = Optional(int)
    login = Optional(str)
    is_admin = Optional(bool, default=False)
    is_baned = Optional(bool, default=False)
    ref_id = Optional(int)
    hero = Optional('Hero')


class Hero(db.Entity):
    _table_ = 'heroes'
    id = PrimaryKey(int, auto=True)
    user_id = Required(User)


class Race(db.Entity):
    _table_ = 'races'
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    desc = Optional(str)
    desc_short = Optional(str)
    class_ = Optional('Class')
    enemy = Optional('Enemy')


class Class(db.Entity):
    _table_ = 'classes'
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    desc = Required(str)
    desc_short = Optional(str)
    main_attr = Optional(str)
    race_id = Required(Race)
    class_bonuses = Set('ClassBonuses')
    enemy = Optional('Enemy')


class ClassBonuses(db.Entity):
    _table_ = 'class_bonuses'
    class_id = Optional(Class)
    type = Optional(str)
    attribute = Optional(str)
    value = Optional(str)
    name = Optional(str)


class Enemy(db.Entity):
    _table_ = 'enemies'
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    rank = Optional(str)
    race_id = Required(Race)
    class_id = Required(Class)
    enemy_inventories = Set('EnemyInventory')
    enemy_items = Set('EnemyItem')
    enemy_skills = Set('EnemySkill')
    enemy_stat = Optional('EnemyStat')
    enemy_team = Optional('EnemyTeam')
    enemy_techniques = Set('EnemyTechnique')
    enemy_weapon = Optional('EnemyWeapon')


class EnemyInventory(db.Entity):
    _table_ = 'enemy_inventory'
    id = PrimaryKey(int, auto=True)
    enemy_id = Required(Enemy)
    item_id = Required('Item')
    count = Required(int, default=1)
    chance = Required(float, default=0)


class EnemyItem(db.Entity):
    _table_ = 'enemy_items'
    id = PrimaryKey(int, auto=True)
    enemy_id = Set(Enemy)
    item_id = Set('Item')
    count = Required(int)


class EnemySkill(db.Entity):
    _table_ = 'enemy_skills'
    id = PrimaryKey(int, auto=True)
    enemy_id = Required(Enemy)
    skill_id = Required('Skill')
    lvl = Optional(int, default=0)


class EnemyStat(db.Entity):
    _table_ = 'enemy_stats'
    id = PrimaryKey(int, auto=True)
    enemy_id = Required(Enemy)
    lvl = Optional(str)
    strength = Optional(int, default=0)
    health = Optional(int, default=0)
    speed = Optional(int, default=0)
    accuracy = Optional(int, default=0)
    dexterity = Optional(int, default=0)
    soul = Optional(int, default=0)
    intelligence = Optional(int, default=0)
    submission = Optional(int, default=0)
    crit_rate = Optional(float, default="0.05")
    crit_damage = Optional(float, default="0.5")
    resist = Optional(float, default="0.1")
    total_stats = Optional(int, default=7)


class EnemyTeam(db.Entity):
    _table_ = 'enemy_teams'
    id = PrimaryKey(int, auto=True)
    enemy_id = Required(Enemy)
    team_id = Set('Team')
    is_leader = Optional(bool)
    prefix = Optional(str, default=" ")


class EnemyTechnique(db.Entity):
    _table_ = 'enemy_technique'
    id = PrimaryKey(int, auto=True)
    enemy_id = Required(Enemy)
    technique_id = Set('Technique')
    lvl = Optional(int, default=0)


class EnemyWeapon(db.Entity):
    _table_ = 'enemy_weapons'
    id = PrimaryKey(int, auto=True)
    enemy_id = Required(Enemy)
    weapon_id = Set('Item')
    lvl = Optional(int, default=0)


class Item(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    desc = Optional(str)
    value = Optional(int)
    type = Optional(str)
    modify = Optional(str)
    class_id = Optional(str)
    enemy_items = Set(EnemyItem)
    enemy_inventory = Set(EnemyInventory)
    enemy_weapon = Optional(EnemyWeapon)


# TODO: Доделать...
class Skill(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    desc = Optional(str)
    value = Optional(int)
    enemy_skill = Set(EnemySkill)


class Team(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    desc = Optional(str)
    value = Optional(int)
    enemy_team = Optional(EnemyTeam)


class Technique(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    desc = Optional(str)
    value = Optional(int)
    enemy_technique = Set(EnemyTechnique)


db.generate_mapping(create_tables=True)
