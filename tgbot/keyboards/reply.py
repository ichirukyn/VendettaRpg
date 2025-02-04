from aiogram.types import KeyboardButton
from aiogram.types import ReplyKeyboardMarkup
from more_itertools import chunked

from tgbot.misc.locale import keyboard
from tgbot.models.entity.enemy import Enemy
from tgbot.models.entity.hero import Hero

# Home
entry_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=keyboard['start'])]],
    resize_keyboard=True)

back_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=keyboard['back'])]],
    resize_keyboard=True)

next_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['next'])],
    ],
    resize_keyboard=True)

home_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['location'])],
        [KeyboardButton(text=keyboard['character'])],
        [KeyboardButton(text=keyboard['top']), KeyboardButton(text=keyboard['settings'])],
    ],
    resize_keyboard=True)

town_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['campus'])],
        [KeyboardButton(text=keyboard['tower']), KeyboardButton(text=keyboard['arena'])],
        # [KeyboardButton(text=keyboard['tower']), KeyboardButton(text=keyboard['arena'])],
        # [KeyboardButton(text=keyboard['fortress']), KeyboardButton(text=keyboard['team'])],
        [KeyboardButton(text=keyboard['shop']), KeyboardButton(text=keyboard['team'])],
        [KeyboardButton(text=keyboard['back'])],
    ],
    resize_keyboard=True)

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['yes'])],
        [KeyboardButton(text=keyboard['back'])],
    ],
    resize_keyboard=True)

# Battle
battle_start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['battle_start']), KeyboardButton(text=keyboard['pass'])],
        [KeyboardButton(text=keyboard['back'])],
    ],
    resize_keyboard=True)

battle_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['technique_list']), KeyboardButton(text=keyboard['spell_list'])],
        [KeyboardButton(text=keyboard['pass']), KeyboardButton(text=keyboard['sub_actions'])],
    ],
    resize_keyboard=True)

battle_sub_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['evasion']), KeyboardButton(text=keyboard['defense'])],
        [KeyboardButton(text=keyboard['counter_strike']), KeyboardButton(text=keyboard['escape'])],
    ],
    resize_keyboard=True)

battle_revival_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=keyboard['reborn'])]],
    resize_keyboard=True)

battle_end_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=keyboard['home'])]],
    resize_keyboard=True)


def list_kb(lists, columns=2, is_back=True):
    kb: [[KeyboardButton]] = []

    for sublist in chunked(lists, columns):
        row = []

        for list in sublist:
            try:
                row.append(KeyboardButton(text=list['name']))
            except:
                row.append(KeyboardButton(text=list.__getattribute__('name')))

        kb.append(row)
    if is_back:
        kb.append([KeyboardButton(text=keyboard['back'])])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def list_object_kb(lists, columns=2):
    kb: [[KeyboardButton]] = []

    for sublist in chunked(lists, columns):
        row = []

        for list in sublist:
            row.append(KeyboardButton(text=list.name))

        kb.append(row)

    kb.append([KeyboardButton(text=keyboard['back'])])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def arena_kb(lists, columns=2):
    kb: [[KeyboardButton]] = []

    for sublist in chunked(lists, columns):
        row = []

        for item in sublist:
            if isinstance(item, Hero) or isinstance(item, Enemy):
                row.append(KeyboardButton(text=item.name))
            else:
                name = item['name']
                fraction = item['fraction']
                text = f"{name}{f': {fraction}' if len(fraction) > 0 else ''}"

                row.append(KeyboardButton(text=text))

        kb.append(row)

    kb.append([KeyboardButton(text=keyboard['back'])])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


arena_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['battle_solo']), KeyboardButton(text=keyboard['battle_group'])],
        [KeyboardButton(text=keyboard['back'])]
    ],

    resize_keyboard=True)

character_distribution_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['strength']), KeyboardButton(text=keyboard['health'])],
        [KeyboardButton(text=keyboard['speed']), KeyboardButton(text=keyboard['dexterity'])],
        [KeyboardButton(text=keyboard['accuracy']), KeyboardButton(text=keyboard['soul'])],
        [KeyboardButton(text=keyboard['intelligence']), KeyboardButton(text=keyboard['submission'])],
        [KeyboardButton(text=keyboard['back'])]
    ],
    resize_keyboard=True)

character_info_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['status']), KeyboardButton(text=keyboard['statistic'])],
        [KeyboardButton(text=keyboard['status_full']), KeyboardButton(text=keyboard['status_flat'])],
        [KeyboardButton(text=keyboard['race']), KeyboardButton(text=keyboard['class'])],
        [KeyboardButton(text=keyboard['back'])]
    ],

    resize_keyboard=True)


def character_kb(free_stats=0):
    kb = [
        [KeyboardButton(text=keyboard['info'])],
        # [KeyboardButton(text=keyboard['equipment']), KeyboardButton(text=keyboard['inventory'])],
        [KeyboardButton(text=keyboard['inventory']), KeyboardButton(text=keyboard['techniques'])],
        # [KeyboardButton(text=keyboard['techniques']), KeyboardButton(text=keyboard['spells'])],
        [KeyboardButton(text=keyboard['back'])]
    ]

    if free_stats > 0:
        kb.insert(0, [KeyboardButton(text=keyboard['distribution'])])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# Equip
equip_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['weapon_current'])],
        [KeyboardButton(text=keyboard['back'])]
    ],

    resize_keyboard=True)

# Inventory
inventory_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['weapon']), KeyboardButton(text=keyboard['potion'])],
        # [KeyboardButton(text=keyboard['technique_book']), KeyboardButton(text=keyboard['spell_book'])],
        # [KeyboardButton(text=keyboard['other'])],
        [KeyboardButton(text=keyboard['back'])]
    ],

    resize_keyboard=True)

# Shop
buy_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['buy_one'])],
        [KeyboardButton(text=keyboard['buy_ten'])],
        [KeyboardButton(text=keyboard['buy_all'])],
        [KeyboardButton(text=keyboard['back'])]
    ],

    resize_keyboard=True)

# Admin
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить характеристику"), KeyboardButton(text="Изменить персонажа")],
        [KeyboardButton(text=keyboard['home'])]
    ],
    resize_keyboard=True)

admin_hero_stats_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сила"), KeyboardButton(text="Контроль")],
        [KeyboardButton(text="Скорость"), KeyboardButton(text="Здоровье")],
        [KeyboardButton(text="Свободные очки"), KeyboardButton(text="Очки охоты")],
        [KeyboardButton(text=keyboard['back'])]
    ],
    resize_keyboard=True)

admin_update_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['next'])],
        [KeyboardButton(text=keyboard['cancel'])],
    ],
    resize_keyboard=True)

# Team
team_accept_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['accept'])],
        [KeyboardButton(text=keyboard['declined'])]
    ],
    resize_keyboard=True)

team_private_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=keyboard['yes'])],
        [KeyboardButton(text=keyboard['no'])]
    ],
    resize_keyboard=True)
