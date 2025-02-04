import unittest
from parameterized import parameterized
from tgbot.models.entity.hero import HeroFactory
from tgbot.models.entity.spells import SpellFactory
from tgbot.models.entity.effects._factory import EffectFactory
from test.models.entity.moc import test_spell_data, speed_to_my, test_hero_data


class TestaValueEffect(unittest.TestCase):
    @parameterized.expand([
        ("number", 20, 20),
        ("percent", 20, 0.2)
    ])
    def test_effects(self, effect_type, base_val, add_val):
        duration = 2
        effect_data = {'duration': duration, 'value': add_val, 'type': effect_type}

        hero = HeroFactory.create_hero(1, test_hero_data, {})
        spell = SpellFactory.create_spell(test_spell_data)

        effect = EffectFactory.create_effect({**speed_to_my, **effect_data}, source='test_1')
        spell.bonuses = [effect]
        hero.spell = spell
        hero.speed = base_val

        # Test base bonus
        hero.spell.activate(hero, hero)
        expected_val = base_val * (1 + add_val) if effect_type == "percent" else base_val + add_val
        self.assertEqual(hero.speed, expected_val)
        self.assertEqual(len(hero.active_bonuses), 1)

        # Test base duration
        for i in range(duration):
            hero.check_active_effects()
            self.assertEqual(hero.speed, expected_val)

        hero.check_active_effects()
        self.assertEqual(hero.speed, base_val)


if __name__ == '__main__':
    unittest.main()
