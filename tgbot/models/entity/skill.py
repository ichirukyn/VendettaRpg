from datetime import datetime, timedelta

from tgbot.models.entity.effect import EffectFactory


class SkillFactory:
    @staticmethod
    def create_skill(hero, data):
        skill_id = data['skill_id']
        name = data['name']
        lvl = data['lvl']
        desc = data['desc']
        duration = data['duration']
        duration_time = data['duration_time']
        nen_type = data['nen_type']
        bonuses = data['bonuses']

        return Skill(hero, skill_id, name, lvl, desc, duration, duration_time, nen_type, bonuses)


class Skill:
    def __init__(self, hero, skill_id, name, lvl, desc, duration, duration_time, nen_type, bonuses):
        self.hero = hero
        self.skill_id = skill_id
        self.name = name
        self.lvl = lvl
        self.desc = desc
        self.nen_type = nen_type
        self.bonuses = bonuses
        self.effects = []

        self.start_time = datetime.now()
        self.duration = duration
        self.duration_time = duration_time

    #  Активация Навыка, при условии, что хватает энергии,
    def skill_activate(self):
        # TODO: Подключить ману к заклинаниям
        if self.hero.mana <= 0:
            return f'Недостаточно Маны для активации.'

        self.skill_apply()

        return f"🔮 {self.hero.name} использовал {self.name}"

    #  Добавление эффектов навыку
    def skill_apply(self):
        for bonus in self.bonuses:
            self.effects.append(bonus)
            bonus.apply(self.hero)

        self.hero.active_bonuses.append(self)

    #  Удаление навыка
    def skill_remove(self):
        for effect in self.effects:
            effect.remove(self.hero)

        for bonus in self.hero.active_bonuses:
            if bonus.name == self.name:
                self.hero.active_bonuses.remove(bonus)

    #  Проверка длительности эффектов навыков
    def skill_check(self):
        print('Check start')
        if self.duration is not None:
            if self.duration == 0:
                self.skill_remove()
            else:
                self.duration -= 1

        if self.duration_time is not None:
            duration_time = timedelta(seconds=self.duration_time)
            time = duration_time + self.start_time
            now = datetime.now()

            if now > time:
                self.skill_remove()


async def skills_init(entity, skills, db):
    i = 0
    new_skill = []

    try:
        for skill in skills:
            skill_id = skill['skill_id']
            bonuses = await db.get_skill_bonuses(skill_id)

            new_bonuses = []

            for bonus in bonuses:
                new_bonuses.append(EffectFactory.create_effect(entity, bonus, source=('skill', skill_id)))

            new_skill.append(dict(skill))
            new_skill[i]['bonuses'] = new_bonuses

            i += 1

        entity.init_skills(new_skill)
        return entity
    except KeyError:
        return entity
