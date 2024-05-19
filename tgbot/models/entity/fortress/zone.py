from tgbot.models.entity.effects._factory import EffectFactory


class ZoneFactory:
    @staticmethod
    def create_zone(data, bonuses):
        id = data.get('id', 1)
        name = data.get('name', 'Лес')
        desc = data.get('desc', 'Описание')
        type = data.get('type', 'forest')

        zone = Zone(id, name, desc, bonuses, type)
        return zone


class Zone:
    def __init__(self, id, name, desc, bonuses, type):
        self.id = id
        self.name = name
        self.desc = desc
        self.type = type

        self.bonuses = bonuses
        self.effects = []
        self.enemies = []


async def zone_init(zone_db):
    try:
        id = zone_db.get('id')
        bonuses = zone_db.get('bonuses', [])

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('zone', id)))

        zone = ZoneFactory.create_zone(zone_db, new_bonuses)

        return zone
    except Exception as e:
        print(f'Zone Error\n{e}')
