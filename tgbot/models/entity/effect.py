import operator
from abc import ABC

from tgbot.dict.technique import condition
from tgbot.dict.technique import condition_attribute
from tgbot.enums.skill import SkillDirection
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

magic_filter = ['intelligence', 'submission', 'soul']


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

        if 'percent' in effect_type:
            return PercentBonusEffect(
                attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
                direction, is_single, every_turn
            )

        if 'number' in effect_type:
            return BonusEffect(
                attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
                direction, is_single, every_turn
            )

        if 'control' in effect_type:
            return ControlEffect(
                attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
                direction, is_single, every_turn
            )

        if 'period' in effect_type:
            return PeriodEffect(
                attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
                direction, is_single, every_turn
            )

        if 'activate' in effect_type:
            return ActivateEffect(
                attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
                direction, is_single, every_turn
            )

        if 'coast' in effect_type:
            return CoastEffect(
                attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
                direction, is_single, every_turn
            )

        if 'shield' in effect_type:
            return ShieldEffect(
                attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
                direction, is_single, every_turn
            )

        if 'heal' in effect_type:
            return HealEffect(
                attribute, value, source, effect_type, name, condition_attribute, condition, condition_value, duration,
                direction, is_single, every_turn
            )

        # raise ValueError(f'{effect_type} -- Не подходящий тип Бонуса')
        print('Не подходящий тип Бонуса')


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

    def cooldown_decrease(self):
        if self.duration_current > 0:
            self.duration_current -= 1

    def check(self, entity, skill=None) -> bool:
        if self.condition_attribute == 'race_id':
            return entity.race.id == self.condition_value
        if self.condition_attribute == 'class_id':
            return entity._class.id == self.condition_value
        if self.condition_attribute is not None:
            return condition_operator[self.condition](getattr(entity, self.condition_attribute),
                                                      int(self.condition_value))

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


class BonusEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        if not hasattr(entity, self.attribute):
            return

        val = getattr(entity, self.attribute) + self.value
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev', val)
        return True

    def cancel(self, hero, target=None, skill=None):
        if self.condition and not self.check(hero):
            return print('Условия не выполнены')

        if not hasattr(hero, self.attribute):
            return

        val = getattr(hero, self.attribute) - self.value
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev', val)


class PercentBonusEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        entity = hero
        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        if not hasattr(entity, self.attribute):
            return

        val = getattr(entity, self.attribute) * (1 + self.value)
        setattr(entity, self.attribute, val)
        setattr(entity, 'prev_percent', val)
        return True

    def cancel(self, hero, target=None, skill=None):
        # TODO: Проверить баффы
        if self.condition and not self.check(hero):
            return print('Условия не выполнены')

        if not hasattr(hero, self.attribute):
            return

        val = getattr(hero, self.attribute) / (1 + self.value)
        setattr(hero, self.attribute, val)
        setattr(hero, 'prev_percent', val)


class ControlEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
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
    def apply(self, hero, target=None, skill=None):
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
    def apply(self, hero, target=None, skill=None):
        entity = hero

        if target is not None and self.direction != 'my':
            entity = target

        if self.condition and not self.check(entity):
            print('Условия не выполнены')
            return False

        return True

    def cancel(self, hero, target=None, skill=None):
        pass


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

        coast_total = self.coast(entity)

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

        coast_total = (control + coast_base) * (1 - control_mod) * (1 + entity.lvl / 50) * coast_rank * damage
        return coast_total

    def info(self, entity, skill=None):
        effect = f"`• {self.name}: {formatted(self.coast(entity, skill))} ({formatted(self.value)})`\n"

        return (
            f"`———————————————————`\n"
            f"{effect}"
        )


class ShieldEffect(Effect, ABC):
    def apply(self, hero, target=None, skill=None):
        shield = self.get_value(hero, skill)

        if self.direction == SkillDirection.my:
            if shield >= hero.shield:
                hero.shield_max = shield
                hero.shield = shield
        else:
            if shield >= target.shield:
                target.shield_max = shield
                target.shield = shield

        hero.update_stats_percent()
        self.add_value = shield

        return True

    def get_value(self, hero, skill=None):
        main_attr = hero.__getattribute__(self.attribute)
        control = hero.control_qi

        element_mod = hero.__getattribute__(skill.type_damage) or 0

        if self.attribute in magic_filter:
            control = hero.control_mana

        # 200 -- На 350 ур. Игрок получит 75% усиления
        shield = self.value + (skill.damage * (main_attr + control) * (1 + hero.lvl / 200) * (1 + hero.shield_modify))
        # Модификатор стихии
        shield *= (1 + element_mod)

        return shield

    def info(self, entity, skill=None):
        effect = f"`• {self.name}: {formatted(self.get_value(entity, skill))} ({formatted(self.value)})`\n"

        return (
            f"`———————————————————`\n"
            f"{effect}"
        )


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
        heal = self.value + (skill.damage * (main_attr + control) * (1 + hero.lvl / 200) * (1 + hero.hp_health_modify))
        # Модификатор стихии
        heal *= (1 + element_mod)

        return heal

    def info(self, entity, skill=None):
        effect = f"`• {self.name}: {formatted(self.get_value(entity, skill))} ({formatted(self.value)})`\n"

        return (
            f"`———————————————————`\n"
            f"{effect}"
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
            bonus.apply(entity, skill=self)

        entity.active_bonuses.append(self)

    def cancel(self, entity):
        for effect in self.effects:
            effect.cancel(entity)
            self.effects.remove(effect)

        if self in entity.active_bonuses:
            entity.active_bonuses.remove(self)
