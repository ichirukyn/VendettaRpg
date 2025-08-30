from abc import ABC

from tgbot.models.entity.effects.effect import Effect


class PercentBonusEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            return False  # Условия не выполнены

        entity.apply_bonus_effect(self.attribute, self.value, is_percent=True)
        self.duration_current = self.duration
        return True

    def cancel(self, hero, target=None, skill=None):
        if self.condition and not self.check(hero):
            return  # Условия не выполнены

        hero.cancel_bonus_effect(self.attribute, self.value, is_percent=True)
