from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from more_itertools import chunked

from tgbot.models.entity.enemy import Enemy
from tgbot.models.entity.hero import Hero

# Home
entry_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Начать")]],
    resize_keyboard=True)

back_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True)

next_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Продолжить")],
    ],
    resize_keyboard=True)

home_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚪 Локации")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🔝 Топ")],
    ],
    resize_keyboard=True)

town_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛕 Небесная башня"), KeyboardButton(text="🏟 Арена")],
        [KeyboardButton(text="🕘 Тренировочная зона"), KeyboardButton(text="🔰 Команды")],
        [KeyboardButton(text="🧺 Торговая лавка")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True)

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True)

# Battle
battle_start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="В бой")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True)

battle_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Атака"), KeyboardButton(text="Навыки")],
        [KeyboardButton(text="Пас")],
    ],
    resize_keyboard=True)

battle_sub_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Уворот"), KeyboardButton(text="Защита")],
        [KeyboardButton(text="Контрудар"), KeyboardButton(text="Сбежать")],
    ],
    resize_keyboard=True)

skill_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Тэн"), KeyboardButton(text="Эн")],
        [KeyboardButton(text="Кэн"), KeyboardButton(text="Гё")],
        [KeyboardButton(text="Шу"), KeyboardButton(text="Рю")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True)

battle_revival_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Возрождение")]],
    resize_keyboard=True)

battle_end_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Домой")]],
    resize_keyboard=True)


def list_kb(lists, columns=2, is_back=True):
    kb: [[KeyboardButton]] = []

    for sublist in chunked(lists, columns):
        row = []

        for list in sublist:
            row.append(KeyboardButton(text=list['name']))

        kb.append(row)
    if is_back:
        kb.append([KeyboardButton(text="🔙 Назад")])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def list_object_kb(lists, columns=2):
    kb: [[KeyboardButton]] = []

    for sublist in chunked(lists, columns):
        row = []

        for list in sublist:
            row.append(KeyboardButton(text=list.name))

        kb.append(row)

    kb.append([KeyboardButton(text="🔙 Назад")])
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

    kb.append([KeyboardButton(text="🔙 Назад")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


arena_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Одиночный бой"), KeyboardButton(text="Командный бой")],
        [KeyboardButton(text="🔙 Назад")]
    ],

    resize_keyboard=True)

# Character
character_train_kb = ReplyKeyboardMarkup(
    keyboard=[
        # [KeyboardButton(text="Обычная тренировка"), KeyboardButton(text="Усиленная тренировка")],
        [KeyboardButton(text="Обычная тренировка")],
        [KeyboardButton(text="🔙 Назад")]
    ],

    resize_keyboard=True)

character_distribution_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сила"), KeyboardButton(text="Здоровье")],
        [KeyboardButton(text="Ловкость"), KeyboardButton(text="Скорость")],
        [KeyboardButton(text="Интеллект"), KeyboardButton(text="Дух")],
        [KeyboardButton(text="Подчинение")],
        [KeyboardButton(text="🔙 Назад")]
    ],

    resize_keyboard=True)


def character_kb(free_stats=0):
    kb = [
        [KeyboardButton(text="Тренировка"), KeyboardButton(text="🏵 Мастерство")],
        [KeyboardButton(text="🧤 Экипировка"), KeyboardButton(text="👝 Инвентарь")],
        [KeyboardButton(text="🔙 Назад")]
    ]

    if free_stats > 0:
        kb.insert(0, [KeyboardButton(text="🎓 Распределение СО")])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# Equip
equip_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Текущее оружие")],
        [KeyboardButton(text="Артефакты (В разработке)")],
        [KeyboardButton(text="🔙 Назад")]
    ],

    resize_keyboard=True)

# Inventory
inventory_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оружие")],
        [KeyboardButton(text="🔙 Назад")]
    ],

    resize_keyboard=True)

# Shop
buy_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Купить всё")],
        [KeyboardButton(text="🔙 Назад")]
    ],

    resize_keyboard=True)

# Hunt
hunt_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зона охоты")],
        [KeyboardButton(text="Дневник охотника (Не доступен)")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True)

hunting_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Продолжить")],
    ],
    resize_keyboard=True)

hunt_action_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Привал"), KeyboardButton(text="Идти дальше")],
        [KeyboardButton(text="Покинуть лес")],
    ],
    resize_keyboard=True)

# Admin
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить характеристику"), KeyboardButton(text="Изменить персонажа")],
        [KeyboardButton(text="Домой")],
    ],
    resize_keyboard=True)

admin_hero_stats_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сила"), KeyboardButton(text="Контроль")],
        [KeyboardButton(text="Скорость"), KeyboardButton(text="Здоровье")],
        [KeyboardButton(text="Свободные очки"), KeyboardButton(text="Очки охоты")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True)

admin_update_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Продолжить")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True)

# Team
team_accept_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Принять")],
        [KeyboardButton(text="Отклонить")]
    ],
    resize_keyboard=True)

team_private_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да")],
        [KeyboardButton(text="Нет")]
    ],
    resize_keyboard=True)
