from tgbot.models.entity.effect import EffectFactory


class RaceFactory:
    @staticmethod
    def create_race(hero, data, bonuses):
        race_id = data['id']
        race_name = data['name']
        race_desc = data['desc']

        race = Race()
        race.init_race(hero, race_id, race_name, race_desc, bonuses)
        return race


class Race:
    hero = None
    race_id = 0
    race_name = ''
    race_desc = ''
    bonuses = []
    effects = []

    def init_race(self, hero, race_id, race_name, race_desc, bonuses):
        self.hero = hero
        self.race_id = race_id
        self.race_name = race_name
        self.race_desc = race_desc
        self.bonuses = bonuses
        self.effects = []

    def race_apply(self):
        for bonus in self.bonuses:
            self.effects.append(bonus)
            bonus.apply(self.hero)

        self.hero.active_bonuses.append(self)


async def race_init(entity, race_id, db):
    try:
        bonuses = await db.get_race_bonuses(race_id)
        race_db = await db.get_race(race_id)

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('race', race_id)))

        race = RaceFactory.create_race(entity, race_db, new_bonuses)
        print(race)

        entity.race = race
        entity.race.race_apply()

        return entity
    except KeyError:
        return entity
