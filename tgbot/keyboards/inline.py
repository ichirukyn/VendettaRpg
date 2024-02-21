from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from more_itertools import chunked

from tgbot.misc.locale import keyboard

back_inline = InlineKeyboardMarkup(row_width=1)

back_inline.add(
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"])
)


# Battle
def arena_inline(lists, columns=2):
    kb = InlineKeyboardMarkup(row_width=2)

    for sublist in chunked(lists, columns):
        row = []

        for item in sublist:
            name = item['name']
            fraction = item['location']
            text = f"{name}{f': {fraction}' if len(fraction) > 0 else ''}"

            button = InlineKeyboardButton(text=text, callback_data=item['id'])
            row.append(button)

        try:
            kb.add(row[0], row[1])
        except IndexError:
            kb.add(row[0])

    kb.add(InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]))

    return kb


def floor_inline(lists, columns=2):
    kb = InlineKeyboardMarkup(row_width=2)

    for sublist in chunked(lists, columns):
        row = []

        for item in sublist:
            name = item['name']
            fraction = item['location']
            text = f"{name}{f': {fraction}' if len(fraction) > 0 else ''}"

            button = InlineKeyboardButton(text=text, callback_data=item['id'])
            row.append(button)

        try:
            kb.add(row[0], row[1])
        except IndexError:
            kb.add(row[0])

    kb.add(InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]))

    return kb


battle_start_inline = InlineKeyboardMarkup(row_width=1)

battle_start_inline.add(
    InlineKeyboardButton(text='В бой', callback_data='В бой'),
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"])
)


# Fortress

def map_nav_inline(is_move=True, is_town=False, is_battle=False, is_exit=False, is_explorer=False):
    map_nav_kb = InlineKeyboardMarkup(row_width=3)

    if is_move:
        map_nav_kb.add(
            InlineKeyboardButton(text='Влево', callback_data='left'),
            InlineKeyboardButton(text='Вперёд', callback_data='up'),
            InlineKeyboardButton(text='Вправо', callback_data='right'),
        )

    if is_town:
        map_nav_kb.add(
            InlineKeyboardButton(text='В город', callback_data='town'),
        )
    if is_battle:
        map_nav_kb.add(
            InlineKeyboardButton(text='В бой', callback_data='battle'),
            InlineKeyboardButton(text='Попробовать сбежать', callback_data='escape'),
        )
    if is_explorer:
        map_nav_kb.add(
            InlineKeyboardButton(text='Исследовать', callback_data='explorer'),
        )
    if is_exit:
        map_nav_kb.add(
            InlineKeyboardButton(text='Выйти', callback_data='exit'),
        )

    return map_nav_kb


fortress_town_inline = InlineKeyboardMarkup(row_width=3)

fortress_town_inline.add(
    InlineKeyboardButton(text='Площадь', callback_data='square'),
    InlineKeyboardButton(text='Таверна', callback_data='tavern'),
)

fortress_town_inline.add(
    InlineKeyboardButton(text='Выйти', callback_data='exit'),
)

# Top
top_inline = InlineKeyboardMarkup(row_width=2)

top_inline.add(
    InlineKeyboardButton(text='Сильнейшие', callback_data='total_stats'),
    InlineKeyboardButton(text='Богатейшие', callback_data='money'),
)
top_inline.add(
    InlineKeyboardButton(text='Сила', callback_data='strength'),
    InlineKeyboardButton(text='Хп', callback_data='health'),
)
top_inline.add(
    InlineKeyboardButton(text='Ловкость', callback_data='dexterity'),
    InlineKeyboardButton(text='Скорость', callback_data='speed'),
)
top_inline.add(
    InlineKeyboardButton(text='Дух', callback_data='soul'),
    InlineKeyboardButton(text='Интеллект', callback_data='intelligence'),
)
top_inline.add(
    InlineKeyboardButton(text='Подчинение', callback_data='submission'),
    InlineKeyboardButton(text='Меткость', callback_data='accuracy'),
)
top_inline.add(
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]),
)

# Character
battle_start_inline = InlineKeyboardMarkup(row_width=1)

battle_start_inline.add(
    InlineKeyboardButton(text='В бой', callback_data='В бой'),
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"])
)


def list_inline(lists, columns=2, label='name', cb_data='id'):
    kb = InlineKeyboardMarkup(row_width=2)

    for sublist in chunked(lists, columns):
        row = []

        for item in sublist:
            if item is None:
                continue

            name = item[label]
            data = item[cb_data]
            button = InlineKeyboardButton(text=name, callback_data=data)

            row.append(button)

        try:
            kb.add(row[0], row[1])
        except IndexError:
            kb.add(row[0])

    kb.add(InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]))

    return kb


# Skills
skill_add_inline = InlineKeyboardMarkup(row_width=1)

skill_add_inline.add(
    InlineKeyboardButton(text='Прикрепить', callback_data='Прикрепить'),
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]),
)

skill_del_inline = InlineKeyboardMarkup(row_width=1)

skill_del_inline.add(
    InlineKeyboardButton(text='Открепить', callback_data='Открепить'),
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]),
)

# Shop
shop_buy_inline = InlineKeyboardMarkup(row_width=1)

shop_buy_inline.add(
    InlineKeyboardButton(text='Купить всё', callback_data='Купить всё'),
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]),
)


# Team
def team_main_inline(is_team=False, is_leader=False):
    kb = InlineKeyboardMarkup(row_width=2)

    if is_team:
        if is_leader:
            kb.add(
                InlineKeyboardButton(text='Добавить игрока', callback_data='Добавить игрока'),
                # InlineKeyboardButton(text='Исключить игрока', callback_data='Исключить игрока'),
            )
            kb.add(
                InlineKeyboardButton(text='Список участников', callback_data='Список участников'),
                InlineKeyboardButton(text='Настройки', callback_data='Настройки'),
            )
        else:
            kb.add(
                InlineKeyboardButton(text='Список участников', callback_data='Список участников'),
                InlineKeyboardButton(text='Выйти из группы', callback_data='Выйти из группы'),
            )
    else:
        kb.add(
            InlineKeyboardButton(text='Создать команду', callback_data='Создать команду'),
            InlineKeyboardButton(text='Все команды', callback_data='Все команды'),
        )

    kb.add(
        InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]),
    )

    return kb


team_setting_inline = InlineKeyboardMarkup(row_width=1)

team_setting_inline.add(
    InlineKeyboardButton(text='Изменить название', callback_data='Изменить название'),
    InlineKeyboardButton(text='Изменить лидера', callback_data='Изменить лидера'),
    InlineKeyboardButton(text='Изменить приватность', callback_data='Изменить приватность'),
    InlineKeyboardButton(text='Распустить', callback_data='Распустить'),
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]),
)

teammate_menu_inline = InlineKeyboardMarkup(row_width=1)

teammate_menu_inline.add(
    InlineKeyboardButton(text='Исключить', callback_data='Исключить'),
    InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]),
    # InlineKeyboardButton(text='Изменить префикс', callback_data='Изменить префикс'),
)

yes_no_inline = InlineKeyboardMarkup(row_width=1)
yes_no_inline.add(
    InlineKeyboardButton(text='Да', callback_data='Да'),
    InlineKeyboardButton(text='Нет', callback_data='Нет'),
)
