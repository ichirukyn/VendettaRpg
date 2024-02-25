import operator
from abc import ABC

from tgbot.dict.technique import condition
from tgbot.dict.technique import condition_attribute
from tgbot.misc.other import formatted
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
        every_turn = data.get('every_turn', False)

        condition_first = data.get('if_first', None)
        condition = data.get('if', None)
        condition_second = data.get('if_second', None)

        if 'percent' in effect_type:
            return PercentBonusEffect(
                attribute, value, source, effect_type, name, condition_first, condition, condition_second, duration,
                direction, is_single, every_turn
            )

        if 'number' in effect_type:
            return BonusEffect(
                attribute, value, source, effect_type, name, condition_first, condition, condition_second, duration,
                direction, is_single, every_turn
            )

        if 'control' in effect_type:
            return ControlEffect(
                attribute, value, source, effect_type, name, condition_first, condition, condition_second, duration,
                direction, is_single, every_turn
            )

        if 'period' in effect_type:
            return PeriodEffect(
                attribute, value, source, effect_type, name, condition_first, condition, condition_second, duration,
                direction, is_single, every_turn
            )

        if 'activate' in effect_type:
            return ActivateEffect(
                attribute, value, source, effect_type, name, condition_first, condition, condition_second, duration,
                direction, is_single, every_turn
            )

        if 'coast' in effect_type:
            return CoastEffect(
                attribute, value, source, effect_type, name, condition_first, condition, condition_second, duration,
                direction, is_single, every_turn
            )

        # # TODO: АоЕ урон сделать:
        # if 'aoe' in effect_type:
        #     return PeriodEffect(
        #         attribute, value, source, effect_type, name, condition_first, condition, condition_second, duration,
        #         direction, is_single, every_turn
        #     )

        raise ValueError(f'{effect_type} -- Не подходящий тип Бонуса')


class Effect(EffectABC, ABC):
    def __init__(self, attribute, value, source, effect_type, name, condition_first, condition, condition_second,
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

        self.condition_first = condition_first
        self.condition = condition
        self.condition_second = condition_second

    def cooldown_decrease(self):
        if self.duration_current > 0:
            self.duration_current -= 1

    def check(self, entity) -> bool:
        if self.condition_first == 'race_id':
            return entity.race.id == self.condition_second
        if self.condition_first == 'class_id':
            return entity._class.id == self.condition_second
        if self.condition_first is not None:
            return condition_operator[self.condition](getattr(entity, self.condition_first), int(self.condition_second))

    def apply(self, hero, target=None) -> bool:
        pass

    def cancel(self, hero, target=None):
        pass

    def info(self, entity):
        el = ''
        if self.condition_second is not None and self.condition is not None:
            val = self.condition_second

            if -1 <= val <= 1:
                val = f'{formatted(val * 100)}%'

            el = f"{condition_attribute[self.condition_first]} {condition[self.condition]} {val}"

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


class BonusEffect(Effect, ABC):
    def apply(self, hero, target=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        val = getattr(entity, self.attribute) + self.value
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev', val)
        return True

    def cancel(self, hero, target=None):
        if self.condition and not self.check(hero):
            return print('Условия не выполнены')

        val = getattr(hero, self.attribute) - self.value
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev', val)


class PercentBonusEffect(Effect, ABC):
    def apply(self, hero, target=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        val = getattr(entity, self.attribute) * (1 + self.value)
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev_percent', val)
        return True

    def cancel(self, hero, target=None):
        # TODO: Проверить баффы
        if self.condition and not self.check(hero):
            return print('Условия не выполнены')

        val = getattr(hero, self.attribute) / (1 + self.value)
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev_percent', val)


class ControlEffect(Effect, ABC):
    def apply(self, hero, target=None):
        if self.condition and not self.check(hero):
            print('Условия не выполнены')
            return False

        self.duration_current = self.duration

        if target.name == hero.name:
            return False

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


class PeriodEffect(Effect, ABC):
    def apply(self, hero, target=None):
        if self.condition and not self.check(hero):
            print('Условия не выполнены')
            return False

        if target.name == hero.name:
            return False

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


class ActivateEffect(Effect, ABC):
    def apply(self, hero, target=None):
        entity = hero

        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        return True

    def cancel(self, hero, target=None):
        pass


class CoastEffect(Effect, ABC):
    def __init__(self, attribute, value, source, effect_type, name, condition_first, condition, condition_second,
                 duration, direction, is_single, every_turn):
        super().__init__(attribute, value, source, effect_type, name, condition_first, condition, condition_second,
                         duration, direction, is_single, every_turn)
        self.rank = 0

    def apply(self, entity, target=None):
        coast_total = self.coast(entity)

        if self.attribute in 'mana':
            entity.mana -= coast_total
        else:
            entity.qi -= coast_total

    def check(self, entity) -> bool:
        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        coast_total = self.coast(entity)

        if self.attribute in 'mana':
            if entity.mana >= coast_total:
                return True
        else:
            if entity.qi >= coast_total:
                return True

        return False

    def coast(self, entity):
        control_mod = entity.control_qi_normalize
        control = entity.control_qi

        if self.attribute in 'mana':
            control_mod = entity.control_mana_normalize
            control = entity.control_mana

        control_mod -= control_mod / 5

        coast_base = self.value
        coast_rank = self.rank

        coast_total = (control + coast_base) * (1 + coast_rank) * (1 - control_mod)
        return coast_total

    def info(self, entity):
        effect = f"`• {self.name}: {formatted(self.coast(entity))} ({formatted(self.value)})`\n"

        return (
            f"`———————————————————`\n"
            f"{effect}"
            f"`• Длительность: {self.duration}`\n"
        )


class EffectParent(EffectParentABC, ABC):
    id = int
    name = str
    desc = str
    desc_short = str

    bonuses = []  # Текущие бонусы
    effects = []  # Активированные бонусы

    def check_effect(self, entity):
        for effect in self.effects:
            if effect.duration_current <= 0 and effect.duration != 0:
                effect.cancel(entity)
                self.effects.remove(effect)

            if effect.is_single and effect.every_turn:
                effect.apply(self)

            effect.cooldown_decrease()

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
            bonus.apply(entity)

        entity.active_bonuses.append(self)

    def cancel(self, entity):
        for effect in self.effects:
            effect.cancel(entity)
            self.effects.remove(effect)

        if self in entity.active_bonuses:
            entity.active_bonuses.remove(self)
