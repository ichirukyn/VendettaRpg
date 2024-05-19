from abc import ABC

from tgbot.enums.skill import SkillDirection
from tgbot.misc.other import formatted
from tgbot.models.entity.effects import magic_filter
from tgbot.models.entity.effects.effect import Effect


class ShieldEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        shield = self.get_value(hero, skill)

        if self.direction == SkillDirection.my:
            if shield >= hero.shield_max:
                hero.shield_max = shield
                hero.shield = shield
            else:
                hero.shield += shield

                if hero.shield >= hero.shield_max:
                    hero.shield = hero.shield_max

            hero.update_stats_percent()
        else:
            if shield >= target.shield_max:
                target.shield_max = shield
                target.shield = shield
            else:
                target.shield += shield

                if target.shield >= target.shield_max:
                    target.shield = target.shield_max

            target.update_stats_percent()

        self.add_value = shield
        return True

    def get_value(self, hero, skill=None):
        main_attr = hero.__getattribute__(self.attribute)
        control = hero.control_qi

        element_mod = hero.__getattribute__(skill.type_damage) or 0

        if self.attribute in magic_filter:
            control = hero.control_mana

        # 200 -- На 350 ур. Игрок получит 75% усиления
        shield = self.value + (skill.damage * (main_attr + control) * (1 + hero.lvl / 200)
                               * (1 + hero.shield_modify)) * (1 + element_mod)

        return shield

    def info(self, entity, skill=None):
        effect = f"`• {self.name}: {formatted(self.get_value(entity, skill))} ({formatted(self.value)})`\n"

        return (
            f"`———————————————————`\n"
            f"{effect}"
        )
