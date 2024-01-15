from datetime import datetime
from datetime import timedelta

from tgbot.models.entity.effect import EffectFactory
from tgbot.models.entity.effect import EffectParent


class SkillFactory:
    @staticmethod
    def create_skill(hero, data):
        skill_id = data['skill_id']
        name = data['name']
        lvl = data['lvl']
        desc = data['desc']
        desc_short = data['desc_short']

        duration = data['duration']
        duration_time = data['duration_time']

        bonuses = data['bonuses']

        return Skill(hero, skill_id, name, lvl, desc, desc_short, duration, duration_time, bonuses)


class Skill(EffectParent):
    def __init__(self, hero, skill_id, name, lvl, desc, desc_short, duration, duration_time, bonuses):
        self.hero = hero
        self.skill_id = skill_id
        self.name = name
        self.lvl = lvl
        self.desc = desc
        self.desc_short = desc_short
        self.bonuses = bonuses
        self.effects = []

        self.start_time = datetime.now()
        self.duration = duration
        self.duration_time = duration_time

    def activate(self):
        # TODO: Подключить ману к заклинаниям
        if self.hero.mana <= 0:
            return f'Недостаточно Маны для активации.'

        self.apply()

        return f"🔮 {self.hero.name} использовал {self.name}"

    def turn_check(self):
        print('Check start')
        if self.duration is not None:
            if self.duration == 0:
                self.cancel()
            else:
                self.duration -= 1

        if self.duration_time is not None:
            duration_time = timedelta(seconds=self.duration_time)
            time = duration_time + self.start_time
            now = datetime.now()

            if now > time:
                self.cancel()


async def skills_init(entity, skills, db):
    i = 0
    new_skill = []

    try:
        for skill in skills:
            skill_id = skill['skill_id']
            bonuses = await db.get_skill_bonuses(skill_id)

            new_bonuses = []

            for bonus in bonuses:
                new_bonuses.append(EffectFactory.create_effect(bonus, source=('skill', skill_id)))

            new_skill.append(dict(skill))
            new_skill[i]['bonuses'] = new_bonuses

            i += 1

        for skill in skills:
            entity.skills.append(SkillFactory.create_skill(entity, skill))

        return entity
    except KeyError:
        return entity
