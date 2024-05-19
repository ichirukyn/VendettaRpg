from abc import ABC

from tgbot.models.entity.effects.effect import Effect


class ControlEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        if self.condition and not self.check(hero):
            print('Условия не выполнены')
            return False

        if target.name == hero.name:
            return False

        self.duration_current = self.duration
        self.target_name = target.name

        if target.effect_chance_check(self.value, hero):
            target.debuff_list.append(
                {
                    'name': self.name,
                    'type': self.type,
                    'attribute': self.attribute,
                    'duration': self.duration,
                    'target': hero,
                })
            return True

        return False

    # def cancel(self, hero, target=None, skill=None):
    #     entity = target
    #
    #     if self.target_name is not None and hero.name == self.target_name:
    #         entity = hero
    #
    #     entity.debuff_list()