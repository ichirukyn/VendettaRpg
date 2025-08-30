from abc import ABC

from tgbot.dict.technique import condition
from tgbot.dict.technique import condition_attribute
from tgbot.misc.other import formatted
from tgbot.models.abstract.effect_abc import EffectABC
from tgbot.models.entity.effects import condition_operator


class Effect(EffectABC, ABC):
    def __init__(self, attribute, value, source, effect_type, name, condition_attribute, condition, condition_value,
                 duration, direction, is_single, every_turn):
        self.attribute = attribute
        self.value = value
        self.source = source
        self.name = name
        self.type = effect_type
        self.duration = duration
        self.duration = duration
        self.duration_current = 0
        self.direction = direction
        self.is_single = is_single
        self.every_turn = every_turn

        self.condition_attribute = condition_attribute
        self.condition = condition
        self.condition_value = condition_value

        self.add_value = 0
        self.target_name = None

    def cooldown_decrease(self):
        if self.duration_current > 0:
            self.duration_current -= 1

    def check(self, entity, skill=None) -> bool:
        if self.condition_attribute == 'race_id':
            return entity.race.id == self.condition_value
        if self.condition_attribute == 'class_id':
            return entity._class.id == self.condition_value
        if self.condition_attribute is not None:
            entity.update_stats_percent()
            return condition_operator[self.condition](getattr(entity, self.condition_attribute), int(self.condition_value))

    def apply(self, hero, target=None, skill=None) -> bool:
        pass

    def cancel(self, hero, target=None, skill=None):
        pass

    def info(self, entity, skill=None):
        el = ''
        if self.condition_value is not None and self.condition is not None:
            val = self.condition_value

            if -1 <= val <= 1:
                val = f'{formatted(val * 100)}%'

            el = f"{condition_attribute[self.condition_attribute]} {condition[self.condition]} {val}"

        el_text = 'Без условий' if self.condition == '' or self.condition is None else el
        value = f'{self.value}'

        if -1 <= self.value <= 1:
            value = f'{formatted(self.value * 100)}%'
        elif self.type == 'percent':
            value = f'{formatted(self.value * 100)}%'

        effect = f"`• {self.name}: {value}`\n"

        if self.type == 'control' or self.type == 'period':
            effect = f"`• {self.name}\nБазовый шанс попадания: {formatted(self.value * 100)}%`\n"

        return (
            f"`———————————————————`\n"
            f"{effect}"
            f"`• Длительность: {self.duration}`\n"
            f"`• Условия: {el_text}`\n"
        )
