from abc import ABC

from tgbot.models.entity.effects.effect import Effect


class BonusEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            # Условия не выполнены
            return False

        val = getattr(entity, self.attribute) + self.value
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev', val)
        self.duration_current = self.duration
        return True

    def cancel(self, hero, target=None, skill=None):
        if self.condition and not self.check(hero):
            # Условия не выполнены
            return

        val = getattr(hero, self.attribute) - self.value
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev', val)
