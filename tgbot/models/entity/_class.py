from tgbot.api.class_ import fetch_class_bonuses
from tgbot.models.entity.effect import EffectFactory
from tgbot.models.entity.effect import EffectParent


class ClassFactory:
    @staticmethod
    def create_class(entity, data, bonuses):
        id = data.get('id', 1)
        name = data.get('name', 'Мечник')
        desc = data.get('desc', 'Мечник')
        desc_short = data.get('desc_short', 'Мечник')
        main_attr = data.get('main_attr', 'strength')
        type = data.get('type', 'Воин')

        _class = Class(entity, id, name, desc, desc_short, bonuses, main_attr, type)
        return _class


class Class(EffectParent):
    main_attr = ''

    def __init__(self, entity, id, name, desc, desc_short, bonuses, main_attr, type):
        self.id = id
        self.name = name
        self.desc_short = desc_short
        self.desc = desc
        self.entity = entity

        self.main_attr = main_attr
        self.type = type

        self.bonuses = bonuses
        self.effects = []


async def class_init(session, entity, class_db):
    try:
        id = class_db.get('id')
        bonuses = await fetch_class_bonuses(session, id)

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('class', id)))

        _class = ClassFactory.create_class(entity, class_db, new_bonuses)

        entity._class = _class
        entity._class.apply()

        return entity
    except KeyError:
        return entity
