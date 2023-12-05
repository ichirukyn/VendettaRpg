from tgbot.models.entity.effect import EffectFactory


class ClassFactory:
    @staticmethod
    def create_class(hero, data, bonuses):
        id = data['id']
        name = data['name']
        desc = data['desc']
        main_attr = data['main_attr']

        _class = Class()
        _class.init_class(hero, id, name, desc, bonuses, main_attr)
        return _class


class Class:
    hero = None
    id = 0
    name = ''
    desc = ''
    bonuses = []
    effects = []
    main_attr = ''

    def init_class(self, hero, id, name, desc, bonuses, main_attr):
        self.hero = hero
        self.id = id
        self.name = name
        self.desc = desc
        self.main_attr = main_attr
        self.bonuses = bonuses
        self.effects = []

    def class_apply(self):
        for bonus in self.bonuses:
            self.effects.append(bonus)
            bonus.apply(self.hero)

        self.hero.active_bonuses.append(self)


async def class_init(entity, id, db):
    try:
        bonuses = await db.get_class_bonuses(id)
        class_db = await db.get_class(id)

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('class', id)))

        _class = ClassFactory.create_class(entity, class_db, new_bonuses)
        # print(_class.name)

        entity._class = _class
        entity._class.class_apply()

        return entity
    except KeyError:
        return entity
