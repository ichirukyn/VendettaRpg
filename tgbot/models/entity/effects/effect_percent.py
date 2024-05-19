from abc import ABC

from tgbot.models.entity.effects.effect import Effect


class PercentBonusEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        val = getattr(entity, self.attribute) * (1 + self.value)
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev_percent', val)
        self.duration_current = self.duration
        return True

    def cancel(self, hero, target=None, skill=None):
        # TODO: Проверить баффы
        if self.condition and not self.check(hero):
            return print('Условия не выполнены')

        val = getattr(hero, self.attribute) / (1 + self.value)
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev_percent', val)
