from tgbot.models.entity.effects._factory import EffectFactory
from tgbot.models.entity.techniques import Technique


class SpellFactory:
    @staticmethod
    def create_spell(data):
        id = data.get('id')
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
        rank = data.get('rank', 1)

        return Spell(id, name, desc, desc_short, damage, type_damage, type_attack, distance, is_stack, type,
                     cooldown, hidden, author, race_id, rank)


class Spell(Technique):
    def check(self, entity) -> bool:
        if self.is_activated(entity) and not self.is_stack:
            self.log = 'Заклинание уже активировано'
            return False

        if self.cooldown_current != 0:
            self.log = f'Заклинание было активировано ранее (КД - {self.cooldown_current} хода)'
            return False

        if not self.effect_check(entity):
            return False

        return True

    def activate(self, entity, target=None) -> str:
        if self.check(entity):
            self.cooldown_current = self.cooldown
            self.apply(entity, target)
            return f"💥 {entity.name} использовал {self.name}\n"
        else:
            return "Заклинание было активирована раньше\n"

    def deactivate(self, entity) -> str:
        self.cancel(entity)
        return f"Заклинание {self.name} было деактивировано"


def spell_init(spell_db):
    try:
        new_bonuses = []

        for bonus in spell_db.get('effects', []):
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('Spell', spell_db.get('spell_id', 0))))

        spell = SpellFactory.create_spell(spell_db)
        spell.bonuses = new_bonuses

        return spell
    except KeyError as e:
        print(e)
        return None
