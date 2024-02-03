from tgbot.api.race import fetch_race_bonuses
from tgbot.models.entity.effect import EffectFactory
from tgbot.models.entity.effect import EffectParent


class RaceFactory:
    @staticmethod
    def create_race(data, bonuses):
        id = data['id']
        name = data['name']
        desc = data['desc']
        desc_short = data['desc_short']

        race = Race()
        race.init_race(id, name, desc, desc_short, bonuses)
        return race


class Race(EffectParent):
    def init_race(self, id, name, desc, desc_short, bonuses):
        self.id = id
        self.name = name
        self.desc = desc
        self.desc_short = desc_short

        self.bonuses = bonuses
        self.effects = []


async def race_init(session, entity, race_db):
    try:
        race_id = race_db.get('id')
        bonuses = await fetch_race_bonuses(session, race_id)

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('race', race_id)))

        race = RaceFactory.create_race(race_db, new_bonuses)

        entity.race = race
        entity.race.apply(entity)

        return entity
    except KeyError:
        return entity
