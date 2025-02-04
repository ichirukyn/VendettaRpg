from abc import ABC

from tgbot.models.abstract.effect_abc import EffectParentABC


class EffectParent(EffectParentABC, ABC):
    id = int
    name = str
    desc = str
    desc_short = str

    bonuses = []  # Текущие бонусы
    effects = []  # Активированные бонусы

    def check_effect(self, entity):
        effects = [*self.effects]

        for effect in self.effects:
            if effect.duration_current <= 0 and effect.duration != 0:
                effect.cancel(entity)
                effects.remove(effect)

            if effect.is_single and effect.every_turn:
                effect.apply(self)

            effect.cooldown_decrease()

        self.effects = effects

    def activate(self, entity) -> str:
        self.apply(entity)
        return f"{self.name} активировано"

    def deactivate(self, entity) -> str:
        self.cancel(entity)
        return f"{self.name} деактивировано"

    def check(self, entity) -> bool:
        pass

    def apply(self, entity):
        for bonus in self.bonuses:
            self.effects.append(bonus)
            bonus.apply(entity, skill=self)

        entity.active_bonuses.append(self)

    def cancel(self, entity):
        for effect in self.effects:
            effect.cancel(entity)
            self.effects.remove(effect)

        if self in entity.active_bonuses:
            entity.active_bonuses.remove(self)
