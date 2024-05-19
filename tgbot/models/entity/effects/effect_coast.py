from abc import ABC

from tgbot.misc.other import formatted
from tgbot.models.entity.effects.effect import Effect


class CoastEffect(Effect, ABC):
    def apply(self, entity, target=None, skill=None):
        coast_total = self.coast(entity, skill)

        if self.attribute in 'mana':
            entity.mana -= coast_total
        else:
            entity.qi -= coast_total

    def check(self, entity, skill=None) -> bool:
        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        coast_total = self.coast(entity, skill)

        if self.attribute in 'mana':
            if entity.mana >= coast_total:
                return True
        else:
            if entity.qi >= coast_total:
                return True

        return False

    def coast(self, entity, skill=None):
        control_mod = entity.control_qi_normalize
        control = entity.control_qi

        if self.attribute in 'mana':
            control_mod = entity.control_mana_normalize
            control = entity.control_mana

        coast_rank = 1
        damage = 1
        if skill is not None and hasattr(skill, 'rank'):
            coast_rank = skill.rank or 1
            damage = skill.damage or 1

        if damage <= 0:
            damage = 1

        control_mod -= control_mod / 7
        coast_base = self.value

        coast_total = (control + coast_base) * (1 - control_mod) * (1 + entity.lvl / 50) * coast_rank * (1 + damage / 100)
        return coast_total

    def info(self, entity, skill=None):
        effect = f"`• {self.name}: {formatted(self.coast(entity, skill))} ({formatted(self.value)})`\n"

        return (
            f"`———————————————————`\n"
            f"{effect}"
        )
