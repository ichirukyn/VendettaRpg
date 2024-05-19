from tgbot.models.entity.effects.effect_activate import ActivateEffect
from tgbot.models.entity.effects.effect_bonus import BonusEffect
from tgbot.models.entity.effects.effect_coast import CoastEffect
from tgbot.models.entity.effects.effect_control import ControlEffect
from tgbot.models.entity.effects.effect_heal import HealEffect
from tgbot.models.entity.effects.effect_hidden import EffectHidden
from tgbot.models.entity.effects.effect_percent import PercentBonusEffect
from tgbot.models.entity.effects.effect_period import PeriodEffect
from tgbot.models.entity.effects.effect_shield import ShieldEffect

effect_map = {
    'percent': PercentBonusEffect,
    'number': BonusEffect,
    'control': ControlEffect,
    'period': PeriodEffect,
    'activate': ActivateEffect,
    'coast': CoastEffect,
    'shield': ShieldEffect,
    'heal': HealEffect,
    'hidden': EffectHidden,
}


class EffectFactory:
    @staticmethod
    def create_effect(data, source):
        effect_type = data.get('type', '')
        attribute = data.get('attribute', '')
        value = data.get('value', 0)
        name = data.get('name', '')
        duration = data.get('duration', None)
        direction = data.get('direction', 'enemy')
        is_single = data.get('is_single', True)
        every_turn = data.get('every_turn', False)

        condition_attribute = data.get('if_first', None)
        condition = data.get('if', None)
        condition_value = data.get('if_second', None)

        # Костыль для спелов
        if data.get('condition', None) is not None:
            condition_attribute = data.get('condition_attribute', None)
            condition = data.get('condition', None)
            condition_value = data.get('condition_value', None)

        effect_class = effect_map.get(effect_type)

        if effect_class is None:
            raise ValueError(f'{effect_type} -- Не подходящий тип Бонуса')

        return effect_class(
            attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
            direction, is_single, every_turn
        )
