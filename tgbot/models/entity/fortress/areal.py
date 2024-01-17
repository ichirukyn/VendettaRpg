from tgbot.models.entity.effect import EffectFactory


class ArealFactory:
    @staticmethod
    def create_areal(data, bonuses):
        id = data.get('id', 1)
        name = data.get('name', 'Лес')
        desc = data.get('desc', 'Описание')
        type = data.get('type', 'forest')

        areal = Areal(id, name, desc, bonuses, type)
        return areal


class Areal:
    def __init__(self, id, name, desc, bonuses, type):
        self.id = id
        self.name = name
        self.desc = desc
        self.type = type

        self.bonuses = bonuses
        self.effects = []
        self.enemies = []


async def areal_init(areal_db):
    try:
        id = areal_db.get('id')
        bonuses = areal_db.get('bonuses', [])

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('areal', id)))

        areal = ArealFactory.create_areal(areal_db, new_bonuses)

        return areal
    except Exception as e:
        print(f'Areal Error\n{e}')
