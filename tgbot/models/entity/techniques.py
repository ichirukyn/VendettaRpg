from copy import deepcopy

from tgbot.misc.other import formatted
from tgbot.models.entity.effect import EffectFactory
from tgbot.models.entity.effect import EffectParent

race_prefix = ['🙂', '🧝‍♂️', '👨‍🦱', '😇', '😈', '☠️']


class TechniqueFactory:
    @staticmethod
    def create_technique(data):
        id = data.get('technique_id')
        name = data.get('name', '')
        desc = data.get('desc', '')
        desc_short = data.get('desc_short', '')
        damage = data.get('damage', 0)
        type_damage = data.get('type_damage', 'none')
        type_attack = data.get('type_attack', 'strength')
        distance = data.get('distance', 'melee')
        is_stack = data.get('is_stack', False)
        type = data.get('type', 'attack')
        race_id = data.get('race_id', 0)
        cooldown = data.get('cooldown', 2)
        hidden = data.get('hidden', False)
        author = data.get('author', 0)

        return Technique(id, name, desc, desc_short, damage, type_damage, type_attack, distance, is_stack, type,
                         cooldown, hidden, author, race_id)


class Technique(EffectParent):
    def __init__(self, id, name, desc, desc_short, damage, type_damage, type_attack, distance, is_stack, type,
                 cooldown, hidden, author, race_id):
        self.id = id
        self.name = name
        self.desc = desc
        self.desc_short = desc_short

        self.damage = damage
        self.type_damage = type_damage
        self.type_attack = type_attack
        self.distance = distance
        self.is_stack = is_stack
        self.type = type
        self.cooldown = cooldown
        self.cooldown_current = 0
        self.hidden = hidden
        self.author = author
        self.race_id = race_id
        self.log = ''

        # Пока без уровней, возможно они будут участвовать позже
        self.lvl = 0

        self.bonuses = []
        self.effects = []
        self.check_prefix()

    def check_prefix(self):
        if isinstance(self.race_id, int):
            prefix = f"{race_prefix[self.race_id - 1]} "
        else:
            prefix = ''
        self.name = prefix + self.name

    def cooldown_decrease(self):
        if self.cooldown_current > 0:
            self.cooldown_current -= 1

    def check(self, entity) -> bool:
        if self.is_activated(entity) and not self.is_stack:
            self.log = 'Техника уже активирована'
            return False

        if self.cooldown_current != 0:
            self.log = f'Техника была активирована ранее (КД - {self.cooldown_current} хода)'
            return False

        if not self.effect_check(entity):
            return False

        return True

    def effect_check(self, entity):
        check = True

        for effect in self.bonuses:
            if effect.type == 'activate' and not effect.check(entity):
                self.log = 'Условия активации не выполнены'
                check = False
            if effect.type == 'coast' and not effect.check(entity):
                self.log = 'Не хватает энергии, чтобы активировать'
                check = False

        return check

    def technique_info(self):
        return (
            f"*{self.name}*\n"
            f"{self.desc}\n"
            f"\n"
            f"`• Урон: {formatted(self.damage * 100)}%\n`"
            f"`• КД: {self.cooldown} {f'(Текущие: {self.cooldown_current})' if self.cooldown_current > 0 else ''}\n`"
            f"`• Дистанция: {'Дальняя' if self.distance == 'distant' else 'Ближняя'}\n`"
            f"`• Тип: {'Поддержка' if self.type == 'distant' else 'Атака'}\n`"
            f"{''.join([effect.info() for effect in self.bonuses])}"
        )

    def activate(self, entity, target=None) -> str:
        if self.check(entity):
            self.cooldown_current = self.cooldown
            self.apply(entity, target)
            return f"💥 {entity.name} использовал {self.name}\n"
        else:
            return "Техника была активирована раньше\n"

    def deactivate(self, entity) -> str:
        self.cancel(entity)
        return f"Техника {self.name} была деактивирована"

    def apply(self, entity, target=None):
        tech = deepcopy(self)

        for bonus in self.bonuses:
            if bonus.direction != 'my' and target is not None:
                is_success = bonus.apply(entity, target)

                if not bonus.is_single and is_success:
                    tech.effects.append(bonus)

            elif bonus.direction == 'my':
                is_success = bonus.apply(entity)

                if not bonus.is_single and is_success:
                    self.effects.append(bonus)

        if len(self.effects) != 0:
            entity.active_bonuses.append(self)

        if target is not None:
            tech.entity = target
            # target.technique = tech

            if len(tech.effects) != 0:
                target.active_bonuses.append(tech)

    def is_activated(self, entity):
        for bonus in entity.active_bonuses:
            if isinstance(bonus, Technique) and bonus.name == self.name and self.cooldown_current == 0:
                return True

        return False


def technique_init(technique_db):
    try:
        new_bonuses = []

        for bonus in technique_db.get('effects', []):
            new_bonuses.append(
                EffectFactory.create_effect(bonus, source=('Technique', technique_db.get('technique_id', 0)))
            )

        technique = TechniqueFactory.create_technique(technique_db)
        technique.bonuses = new_bonuses

        return technique
    except KeyError as e:
        print(e)
        return None


def copy_to_depth(orig, depth):
    copy_dict = {}
    for key, value in orig.__dict__.items():
        if isinstance(value, dict) and depth > 0:
            copy_dict[key] = copy_to_depth(value, depth - 1)
        elif isinstance(value, Technique) and depth > 0:
            copy_dict[key] = copy_to_depth(value, depth - 1)
        else:
            copy_dict[key] = value
    return copy_dict
