from abc import ABC

from tgbot.misc.other import formatted
from tgbot.models.entity.effects import magic_filter
from tgbot.models.entity.effects.effect import Effect


class HealEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        heal = self.get_value(hero, skill)
        entity = hero

        if target is not None:
            entity = target

        if self.duration == 'my':
            entity.hp += heal
            if heal >= entity.hp_max:
                entity.hp = entity.hp_max
        else:
            entity.hp += heal
            if heal >= entity.hp_max:
                entity.hp = entity.hp_max

        entity.update_stats_percent()
        self.add_value = heal

        return True

    def get_value(self, hero, skill=None):
        main_attr = hero.__getattribute__(self.attribute)
        control = hero.control_qi

        element_mod = hero.__getattribute__(skill.type_damage) or 0

        if self.attribute in magic_filter:
            control = hero.control_mana

        # 200 -- На 350 ур. Игрок получит 75% усиления
        heal = self.value + (skill.damage * (main_attr + control) * (1 + hero.lvl / 200)
                             * (1 + hero.hp_health_modify)) * (1 + element_mod)

        return heal

    def info(self, entity, skill=None):
        effect = f"`• {self.name}: {formatted(self.get_value(entity, skill))} ({formatted(self.value)})`\n"

        return (
            f"`———————————————————`\n"
            f"{effect}"
        )
