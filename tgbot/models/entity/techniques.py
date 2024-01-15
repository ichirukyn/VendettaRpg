from copy import deepcopy

from tgbot.models.entity.effect import EffectFactory
from tgbot.models.entity.effect import EffectParent


class TechniqueFactory:
    @staticmethod
    def create_technique(entity, data):
        id = data.get('technique_id')
        name = data.get('name')
        desc = data.get('desc')
        desc_short = data.get('desc_short')
        damage = data.get('damage')
        type_damage = data.get('type_damage')
        distance = data.get('distance')
        is_stack = data.get('is_stack')
        type = data.get('type', 'attack')
        cooldown = data.get('cooldown')

        return Technique(entity, id, name, desc, desc_short, damage, type_damage, distance, is_stack, type, cooldown)


class Technique(EffectParent):
    def __init__(self, entity, id, name, desc, desc_short, damage, type_damage, distance, is_stack, type, cooldown):
        self.id = id
        self.name = name
        self.desc = desc
        self.desc_short = desc_short

        self.entity = entity
        self.damage = damage
        self.type_damage = type_damage
        self.distance = distance
        self.is_stack = is_stack
        self.type = type
        self.cooldown = cooldown
        self.cooldown_current = 0

        # Пока без уровней, возможно они будут участвовать позже
        self.lvl = 0

        self.bonuses = []
        self.effects = []

    def cooldown_decrease(self):
        if self.cooldown_current > 0:
            self.cooldown_current -= 1

    def check(self) -> bool:
        if not self.is_activated() or self.is_stack:
            if self.cooldown_current == 0:
                return True

        return False

    def activate(self, target=None) -> str:
        if self.check:
            self.cooldown_current = self.cooldown
            self.apply(target)
            return f"💥 {self.entity.name} использовал {self.name}\n"
        else:
            return "Техника была активирована раньше\n"

    def deactivate(self) -> str:
        self.cancel()
        return f"Техника {self.name} была деактивирована"

    def apply(self, target=None):
        tech = deepcopy(self)

        for bonus in self.bonuses:
            if bonus.direction != 'my' and target is not None:
                bonus.target = target

            if not bonus.is_single:
                if bonus.apply(self.entity) and bonus.direction == 'my':
                    self.effects.append(bonus)
                else:
                    tech.effects.append(bonus)
            else:
                bonus.apply(self.entity)

        if len(self.effects) != 0:
            self.entity.active_bonuses.append(self)

        if target is not None:
            tech.entity = target
            target.technique = tech

            if len(tech.effects) != 0:
                target.active_bonuses.append(tech)

    def is_activated(self):
        for bonus in self.entity.active_bonuses:
            if isinstance(bonus, Technique) and bonus.name == self.name and self.cooldown_current == 0:
                return True

        return False


def technique_init(entity, technique_db, technique_bonuses):
    try:
        new_bonuses = []

        for bonus in technique_bonuses:
            new_bonuses.append(
                EffectFactory.create_effect(bonus, source=('Technique', technique_db.get('technique_id', 0)))
            )

        technique = TechniqueFactory.create_technique(entity, technique_db)
        technique.bonuses = new_bonuses

        return technique
    except KeyError as e:
        print(e)
        return None
