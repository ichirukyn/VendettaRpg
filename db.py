from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int]
    login: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_baned: Mapped[bool] = mapped_column(default=False)
    ref_id: Mapped[int] = mapped_column(default=1)


class Hero(Base):
    __tablename__ = 'heroes'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column()
    clan: Mapped[str] = mapped_column()
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"))
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    rank: Mapped[str] = mapped_column()
    money: Mapped[int] = mapped_column(default='5000')
    limit_os: Mapped[int] = mapped_column(default=0)
    evolution: Mapped[int] = mapped_column(default=0)


class Race(Base):
    __tablename__ = 'races'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    desc: Mapped[str] = mapped_column()
    desc_short: Mapped[Optional[str]] = mapped_column()


class Class(Base):
    __tablename__ = 'classes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    desc: Mapped[str]
    desc_short: Mapped[Optional[str]]
    main_attr: Mapped[str]
    race_id: Mapped[Race] = mapped_column(ForeignKey("races.id"))


class ClassBonuses(Base):
    __tablename__ = 'class_bonuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    type: Mapped[str]
    attribute: Mapped[str]
    value: Mapped[int]
    name: Mapped[str]


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    desc: Mapped[str]
    value: Mapped[int]
    # desc_short: Mapped[Optional[str]]
    type: Mapped[str]
    modify: Mapped[int]
    class_id: Mapped[int] = mapped_column(ForeignKey('classes.id'))


# TODO: Доделать...
class Skill(Base):
    __tablename__ = 'enemy_weapons'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    desc: Mapped[str]
    value: Mapped[int]


# TODO: Доделать...
class Team(Base):
    __tablename__ = 'enemy_weapons'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    desc: Mapped[str]
    value: Mapped[int]


# TODO: Доделать...
class Technique(Base):
    __tablename__ = 'enemy_weapons'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    desc: Mapped[str]
    value: Mapped[int]


class Enemy(Base):
    __tablename__ = 'enemies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    rank: Mapped[str] = mapped_column(default='Обычный')
    race_id: Mapped[int] = mapped_column(ForeignKey('races.id'))
    class_id: Mapped[int] = mapped_column(ForeignKey('classes.id'))


class EnemyInventory(Base):
    __tablename__ = 'enemy_inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    enemy_id: Mapped[int] = mapped_column(ForeignKey('enemies.id'))
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    count: Mapped[int] = mapped_column(default=1)
    chance: Mapped[float] = mapped_column(default=0)


class EnemyItem(Base):
    __tablename__ = 'enemy_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    enemy_id: Mapped[int] = mapped_column(ForeignKey('enemies.id'))
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    count: Mapped[int] = mapped_column(default=1)


class EnemySkill(Base):
    __tablename__ = 'enemy_skills'

    id: Mapped[int] = mapped_column(primary_key=True)
    enemy_id: Mapped[int] = mapped_column(ForeignKey('enemies.id'))
    skill_id: Mapped[int] = mapped_column(ForeignKey('skills.id'))
    lvl: Mapped[int] = mapped_column(default=0)


class EnemyStat(Base):
    __tablename__ = 'enemy_stats'

    id: Mapped[int] = mapped_column(primary_key=True)
    enemy_id: Mapped[int] = mapped_column(ForeignKey('enemies.id'))
    lvl: Mapped[int] = mapped_column(default=1)
    strength: Mapped[int] = mapped_column(default=0)
    health: Mapped[int] = mapped_column(default=0)
    speed: Mapped[int] = mapped_column(default=0)
    accuracy: Mapped[int] = mapped_column(default=0)
    dexterity: Mapped[int] = mapped_column(default=0)
    soul: Mapped[int] = mapped_column(default=0)
    intelligence: Mapped[int] = mapped_column(default=0)
    submission: Mapped[int] = mapped_column(default=0)
    crit_rate: Mapped[float] = mapped_column(default="0.05")
    crit_damage: Mapped[float] = mapped_column(default="0.5")
    resist: Mapped[float] = mapped_column(default="0.1")
    total_stats: Mapped[int] = mapped_column(default=7)


class EnemyTeam(Base):
    __tablename__ = 'enemy_teams'

    id: Mapped[int] = mapped_column(primary_key=True)
    enemy_id: Mapped[int] = mapped_column(ForeignKey('enemies.id'))
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'))
    is_leader: Mapped[bool]
    prefix: Mapped[str] = mapped_column(default=" ")


class EnemyTechnique(Base):
    __tablename__ = 'enemy_technique'

    id: Mapped[int] = mapped_column(primary_key=True)
    enemy_id: Mapped[int] = mapped_column(ForeignKey('enemies.id'))
    technique_id: Mapped[int] = mapped_column(ForeignKey('techniques.id'))
    lvl: Mapped[int] = mapped_column(default=0)


class EnemyWeapon(Base):
    __tablename__ = 'enemy_weapons'

    id: Mapped[int] = mapped_column(primary_key=True)
    enemy_id: Mapped[int] = mapped_column(ForeignKey('enemies.id'))
    weapon_id: Mapped[int] = mapped_column(ForeignKey('weapons.id'))
    lvl: Mapped[int] = mapped_column(default=0)
