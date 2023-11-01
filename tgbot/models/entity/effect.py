class EffectFactory:
    @staticmethod
    def create_effect(data, source):
        effect_type = data['type']
        attribute = data['attribute']
        value = data['value']
        name = data['name']

        if 'percent' in effect_type:
            return PercentBonusEffect(attribute, value, source, effect_type, name)

        if 'off' in effect_type or 'on' in effect_type:
            return ToggleBonusEffect(attribute, value, source, effect_type, name)

        if 'number' in effect_type:
            return BonusEffect(attribute, value, source, effect_type, name)


class Effect:
    def __init__(self, attribute, value, source, effect_type, name):
        self.attribute = attribute
        self.value = value
        self.source = source
        self.name = name
        self.type = effect_type

    def apply(self, hero):
        pass

    def remove(self, hero):
        pass


class BonusEffect(Effect):
    def apply(self, hero):
        setattr(hero, self.attribute, getattr(hero, self.attribute) + self.value)

    def remove(self, hero):
        setattr(hero, self.attribute, getattr(hero, self.attribute) - self.value)


class PercentBonusEffect(Effect):
    def apply(self, hero):
        setattr(hero, self.attribute, getattr(hero, self.attribute) * (1 + self.value))

    def remove(self, hero):
        # TODO: Проверить баффы
        # match = (getattr(hero, self.attribute) * 100) / self.value
        setattr(hero, self.attribute, getattr(hero, self.attribute) / (1 + self.value))


class ToggleBonusEffect(Effect):
    def apply(self, hero):
        bonuses = []

        for bonus in hero.active_bonuses:
            if bonus.name != self.attribute:
                bonuses.append(bonus)
            else:
                bonus.remove(hero)

        hero.active_bonuses = bonuses

    # def remove(self, hero):
    #     for skill in hero.skills:
    #         if skill.name == self.attribute:
    #             skill.skill_apply()
