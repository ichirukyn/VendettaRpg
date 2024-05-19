from tgbot.api.class_ import fetch_class_bonuses
from tgbot.models.entity.effects._factory import EffectFactory
from tgbot.models.entity.effects.effect_parent import EffectParent


class ClassFactory:
    @staticmethod
    def create_class(data, bonuses):
        id = data.get('id', 1)
        name = data.get('name', 'Мечник')
        desc = data.get('desc', 'Мечник')
        desc_short = data.get('desc_short', 'Мечник')
        main_attr = data.get('main_attr', 'strength')
        type = data.get('type', 'Воин')

        _class = Class(id, name, desc, desc_short, bonuses, main_attr, type)
        return _class


class Class(EffectParent):
    main_attr = ''

    def __init__(self, id, name, desc, desc_short, bonuses, main_attr, type):
        self.id = id
        self.name = name
        self.desc_short = desc_short
        self.desc = desc

        self.main_attr = main_attr
        self.type = type

        self.bonuses = bonuses
        self.effects = []


async def class_init(session, class_db):
    try:
        id = class_db.get('id')
        bonuses = await fetch_class_bonuses(session, id)

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('class', id)))

        _class = ClassFactory.create_class(class_db, new_bonuses)
        return _class
    except KeyError:
        return None
