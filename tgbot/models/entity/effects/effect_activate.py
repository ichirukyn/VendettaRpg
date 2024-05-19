from abc import ABC

from tgbot.models.entity.effects.effect import Effect


class ActivateEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        entity = hero
        self.duration_current = self.duration

        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        return True

    def cancel(self, hero, target=None, skill=None):
        pass
