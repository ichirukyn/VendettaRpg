from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from more_itertools import chunked

back_inline = InlineKeyboardMarkup(row_width=1)

back_inline.add(
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад')
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

    kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'))

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

    kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'))

    return kb


battle_start_inline = InlineKeyboardMarkup(row_width=1)

battle_start_inline.add(
    InlineKeyboardButton(text='В бой', callback_data='В бой'),
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад')
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
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'),
)

# Character
battle_start_inline = InlineKeyboardMarkup(row_width=1)

battle_start_inline.add(
    InlineKeyboardButton(text='В бой', callback_data='В бой'),
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад')
)


def list_inline(lists, columns=2, label='name', cb_data='id'):
    kb = InlineKeyboardMarkup(row_width=2)

    for sublist in chunked(lists, columns):
        row = []

        for item in sublist:
            name = item[label]
            data = item[cb_data]
            button = InlineKeyboardButton(text=name, callback_data=data)

            row.append(button)

        try:
            kb.add(row[0], row[1])
        except IndexError:
            kb.add(row[0])

    kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'))

    return kb


# Skills
skill_add_inline = InlineKeyboardMarkup(row_width=1)

skill_add_inline.add(
    InlineKeyboardButton(text='Прикрепить', callback_data='Прикрепить'),
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'),
)

skill_del_inline = InlineKeyboardMarkup(row_width=1)

skill_del_inline.add(
    InlineKeyboardButton(text='Открепить', callback_data='Открепить'),
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'),
)

# Shop
shop_buy_inline = InlineKeyboardMarkup(row_width=1)

shop_buy_inline.add(
    InlineKeyboardButton(text='Купить всё', callback_data='Купить всё'),
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'),
)

# Hunt
hunt_inline = InlineKeyboardMarkup(row_width=1)

hunt_inline.add(
    InlineKeyboardButton(text='Зона охоты', callback_data='Зона охоты'),
    InlineKeyboardButton(text='Дневник охотника (Не доступен)', callback_data='(Не доступен)'),
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'),
)

hunt_action_inline = InlineKeyboardMarkup(row_width=2)

hunt_action_inline.add(
    InlineKeyboardButton(text='Идти дальше', callback_data='Идти дальше'),
)

hunt_action_inline.add(
    InlineKeyboardButton(text='Покинуть лес', callback_data='Покинуть лес'),
)

hunt_battle_inline = InlineKeyboardMarkup(row_width=2)

hunt_battle_inline.add(
    InlineKeyboardButton(text='В бой', callback_data='В бой'),
)


# hunting_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="Продолжить")],
#     ],
#     resize_keyboard=True)


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
        InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'),
    )

    return kb


team_setting_inline = InlineKeyboardMarkup(row_width=1)

team_setting_inline.add(
    InlineKeyboardButton(text='Изменить название', callback_data='Изменить название'),
    InlineKeyboardButton(text='Изменить лидера', callback_data='Изменить лидера'),
    InlineKeyboardButton(text='Изменить приватность', callback_data='Изменить приватность'),
    InlineKeyboardButton(text='Распустить', callback_data='Распустить'),
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'),
)

teammate_menu_inline = InlineKeyboardMarkup(row_width=1)

teammate_menu_inline.add(
    InlineKeyboardButton(text='Исключить', callback_data='Исключить'),
    InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад'),
    # InlineKeyboardButton(text='Изменить префикс', callback_data='Изменить префикс'),
)

yes_no_inline = InlineKeyboardMarkup(row_width=1)
yes_no_inline.add(
    InlineKeyboardButton(text='Да', callback_data='Да'),
    InlineKeyboardButton(text='Нет', callback_data='Нет'),
)
