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
        self.direction = direction
        self.is_single = is_single

        self.condition_first = condition_first
        self.condition = condition
        self.condition_second = condition_second

    def check(self) -> bool:
        if self.condition_first is not None:
            return condition_operator[self.condition](self.condition_first, self.condition_second)

    def apply(self, hero, target=None) -> bool:
        pass

    def remove(self, hero, target=None):
        pass


class BonusEffect(Effect, ABC):
    def apply(self, hero, target=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check():
            print('Условия не выполнены')
            return False

        val = getattr(entity, self.attribute) + self.value
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev', val)
        return True

    def remove(self, hero, target=None):
        if self.condition and not self.check():
            return print('Условия не выполнены')

        val = getattr(hero, self.attribute) - self.value
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev', val)


class PercentBonusEffect(Effect, ABC):
    def apply(self, hero, target=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check():
            print('Условия не выполнены')
            return False

        val = getattr(entity, self.attribute) * (1 + self.value)
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev_percent', val)
        return True

    def remove(self, hero, target=None):
        # TODO: Проверить баффы
        if self.condition and not self.check():
            return print('Условия не выполнены')

        val = getattr(hero, self.attribute) / (1 + self.value)
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev_percent', val)


class ControlEffect(Effect, ABC):
    def apply(self, hero, target=None):
        if self.condition and not self.check():
            print('Условия не выполнены')
            return False

        if target.effect_chance_check(self.value, hero):
            target.debuff_list.append(
                {'type': self.type, 'duration': self.duration, 'target': hero, 'name': self.name}.copy())
            return True


class PeriodEffect(Effect, ABC):
    def apply(self, hero, target=None):
        if self.condition and not self.check():
            print('Условия не выполнены')
            return False

        if target.effect_chance_check(self.value, hero):
            target.debuff_list.append({
                'name': self.name,
                'type': self.type,
                'duration': self.duration,
                'element': self.attribute,
                'damage': self.value,
                'target': hero,
            })
            return True


class EffectParent(EffectParentABC, ABC):
    id = int
    name = str
    desc = str
    desc_short = str
    entity = None

    bonuses = []  # Текущие бонусы
    effects = []  # Активированные бонусы

    def activate(self, target=None) -> str:
        self.apply()
        return f"{self.name} активировано"

    def deactivate(self) -> str:
        self.remove()
        return f"{self.name} деактивировано"

    def check(self) -> bool:
        pass

    def apply(self, target=None):
        for bonus in self.bonuses:
            self.effects.append(bonus)
            bonus.apply(self.entity, target)

        self.entity.active_bonuses.append(self)

    def remove(self):
        for effect in self.bonuses:
            effect.remove(self.entity)
            self.effects.remove(effect)

        self.entity.active_bonuses.remove(self)

# Под вопросом
# class ToggleBonusEffect(Effect):
#     def apply(self, hero):
#         bonuses = []
#
#         for bonus in hero.active_bonuses:
#             if bonus.name != self.attribute:
#                 bonuses.append(bonus)
#             else:
#                 bonus.remove(hero)
#
#         hero.active_bonuses = bonuses
#
#     # def remove(self, hero):
#     #     for skill in hero.skills:
#     #         if skill.name == self.attribute:
#     #             skill.skill_apply()
