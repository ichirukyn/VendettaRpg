from tgbot.api.race import fetch_race_bonuses
from tgbot.api.race import get_race
from tgbot.models.entity.effect import EffectFactory
from tgbot.models.entity.effect import EffectParent


class RaceFactory:
    @staticmethod
    def create_race(entity, data, bonuses):
        id = data['id']
        name = data['name']
        desc = data['desc']
        desc_short = data['desc_short']

        race = Race()
        race.init_race(entity, id, name, desc, desc_short, bonuses)
        return race


class Race(EffectParent):
    def init_race(self, entity, id, name, desc, desc_short, bonuses):
        self.id = id
        self.name = name
        self.desc = desc
        self.desc_short = desc_short
        self.entity = entity

        self.bonuses = bonuses
        self.effects = []


def race_init(entity, race_id):
    try:
        bonuses = fetch_race_bonuses(race_id)
        race_db = get_race(race_id).json

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('race', race_id)))

        race = RaceFactory.create_race(entity, race_db, new_bonuses)

        entity.race = race
        entity.race.apply()

        return entity
    except KeyError:
        return entity
