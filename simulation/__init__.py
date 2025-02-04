from tgbot.models.entity.techniques import TechniqueFactory

base_technique_config = {
    'id': 1,
    'name': 'Удар',
    'desc': 'Удар',
    'damage': 0.5,
    'type_damage': 'none',
    'type_attack': 'all',
    'distance': 'melee',
    'is_stack': False,
    'type': 'attack',
    'cooldown': 0,
    'rank': 1,
}

base_technique = TechniqueFactory.create_technique(base_technique_config)
