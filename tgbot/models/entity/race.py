from tgbot.api.race import fetch_race_bonuses
from tgbot.models.entity.effects._factory import EffectFactory
from tgbot.models.entity.effects.effect_parent import EffectParent


class RaceFactory:
    @staticmethod
    def create_race(data, bonuses):
        id = data['id']
        name = data['name']
        desc = data['desc']
        desc_short = data['desc_short']
        tag_id = data['tag_id']

        race = Race()
        race.init_race(id, name, desc, desc_short, bonuses, tag_id)
        return race


class Race(EffectParent):
    def init_race(self, id, name, desc, desc_short, bonuses, tag_id):
        self.id = id
        self.name = name
        self.desc = desc
        self.desc_short = desc_short

        self.bonuses = bonuses
        self.effects = []
        self.tag_id = tag_id


async def race_init(session, race_db):
    try:
        id = race_db.get('id')

        bonuses = race_db.get('bonuses', None)

        if bonuses is None:
            bonuses = await fetch_race_bonuses(session, id)

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('race', id)))

        race = RaceFactory.create_race(race_db, new_bonuses)
        return race
    except KeyError:
        return None
