test_hero_data = {
    "name": 'Ichiru',
    "rank": 'Редкий',
    "speed": 20,
    "money": 50,
    "chat_id": 792451145,
}

test_spell_data = {
    'name': 'test',
    'damage': 0,
}

speed_to_my = {
    'name': 'Ускорение',
    'attribute': 'speed',
    'duration': 2,
    'direction': 'my',
    'is_single': False,
}

test_number_effect = {
    **speed_to_my,
    'type': 'number',
}
