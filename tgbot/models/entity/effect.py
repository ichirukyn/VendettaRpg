import operator
from abc import ABC

from tgbot.models.abstract.effect_abc import EffectABC
from tgbot.models.abstract.effect_abc import EffectParentABC

condition_operator = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne
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

        condition_first = data.get('if_first', None)
        condition = data.get('if', None)
        condition_second = data.get('if_second', None)

        if 'percent' in effect_type:
            return PercentBonusEffect(attribute, value, source, effect_type, name,
                                      condition_first, condition, condition_second, duration, direction, is_single)

        # if 'off' in effect_type or 'on' in effect_type:
        #     return ToggleBonusEffect(attribute, value, source, effect_type, name,
        #                              condition_first, condition, condition_second)

        if 'number' in effect_type:
            return BonusEffect(attribute, value, source, effect_type, name,
                               condition_first, condition, condition_second, duration, direction, is_single)

        if 'control' in effect_type:
            return ControlEffect(attribute, value, source, effect_type, name,
                                 condition_first, condition, condition_second, duration, direction, is_single)

        if 'period' in effect_type:
            return PeriodEffect(attribute, value, source, effect_type, name,
                                condition_first, condition, condition_second, duration, direction, is_single)

        raise f'{effect_type} -- Не подходящий тип Бонуса'


class Effect(EffectABC, ABC):
    def __init__(self, attribute, value, source, effect_type, name, condition_first, condition, condition_second,
                 duration, direction, is_single):
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

        self.condition_first = condition_first
        self.condition = condition
        self.condition_second = condition_second
        self.target = None

    def cooldown_decrease(self):
        if self.duration_current > 0:
            self.duration_current -= 1

    def check(self) -> bool:
        if self.condition_first is not None:
            return condition_operator[self.condition](self.condition_first, self.condition_second)

    def apply(self, hero) -> bool:
        pass

    def cancel(self, hero):
        pass


class BonusEffect(Effect, ABC):
    def apply(self, hero):
        entity = hero
        if self.target is not None and self.direction != 'my':
            entity = self.target

        if self.condition and not self.check():
            print('Условия не выполнены')
            return False

        val = getattr(entity, self.attribute) + self.value
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev', val)
        return True

    def cancel(self, hero):
        if self.condition and not self.check():
            return print('Условия не выполнены')

        val = getattr(hero, self.attribute) - self.value
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev', val)


class PercentBonusEffect(Effect, ABC):
    def apply(self, hero):
        entity = hero
        if self.target is not None and self.direction != 'my':
            entity = self.target

        if self.condition and not self.check():
            print('Условия не выполнены')
            return False

        val = getattr(entity, self.attribute) * (1 + self.value)
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev_percent', val)
        return True

    def cancel(self, hero):
        # TODO: Проверить баффы
        if self.condition and not self.check():
            return print('Условия не выполнены')

        val = getattr(hero, self.attribute) / (1 + self.value)
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev_percent', val)


class ControlEffect(Effect, ABC):
    def apply(self, hero):
        if self.condition and not self.check():
            print('Условия не выполнены')
            return False

        self.duration_current = self.duration

        if self.target.effect_chance_check(self.value, hero):
            self.target.debuff_list.append(
                {
                    'name': self.name,
                    'type': self.type,
                    'attribute': self.attribute,
                    'duration': self.duration,
                    'target': hero,
                }.copy())
            return True


class PeriodEffect(Effect, ABC):
    def apply(self, hero):
        if self.condition and not self.check():
            print('Условия не выполнены')
            return False

        if self.target.effect_chance_check(self.value, hero):
            self.target.debuff_list.append(
                {
                    'name': self.name,
                    'type': self.type,
                    'element': self.attribute,
                    'duration': self.duration,
                    'target': hero,
                }.copy())
            return True


class EffectParent(EffectParentABC, ABC):
    id = int
    name = str
    desc = str
    desc_short = str
    entity = None

    bonuses = []  # Текущие бонусы
    effects = []  # Активированные бонусы

    def check_effect(self):
        for effect in self.effects:
            if effect.duration_current <= 0 and effect.duration != 0:
                effect.cancel(self.entity)
                self.effects.remove(effect)

            effect.cooldown_decrease()

    def activate(self) -> str:
        self.apply()
        return f"{self.name} активировано"

    def deactivate(self) -> str:
        self.cancel()
        return f"{self.name} деактивировано"

    def check(self) -> bool:
        pass

    def apply(self):
        for bonus in self.bonuses:
            self.effects.append(bonus)
            bonus.apply(self.entity)

        self.entity.active_bonuses.append(self)

    def cancel(self):
        for effect in self.effects:
            effect.cancel(self.entity)
            self.effects.remove(effect)

        if self in self.entity.active_bonuses:
            self.entity.active_bonuses.remove(self)
