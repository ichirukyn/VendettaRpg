from abc import ABC

from tgbot.models.entity.effects.effect import Effect


class PeriodEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        if self.condition and not self.check(hero):
            # Условия не выполнены
            return False

        if target.name == hero.name:
            return False

        self.duration_current = self.duration

        if target.effect_chance_check(self.value, hero):
            target.debuff_list.append(
                {
                    'name': self.name,
                    'type': self.type,
                    'element': self.attribute,
                    'duration': self.duration,
                    'target': hero,
                })
            return True

        return False
