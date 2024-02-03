from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from tgbot.handlers.battle.interface import BattleFactory
from tgbot.handlers.location import to_home
from tgbot.keyboards.inline import fortress_town_inline
from tgbot.keyboards.inline import map_nav_inline
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import town_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import FortressState
from tgbot.misc.state import LocationState
from tgbot.models.entity.enemy import init_enemy
from tgbot.models.entity.map import Map
from tgbot.models.entity.map import MapFactory
from tgbot.models.user import DBCommands


async def battle_init(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    session = message.bot.get('session')
    data = await state.get_data()

    enemy_team = data.get('enemy_team')
    player_team = data.get('player_team')

    if player_team:
        player_team_update = []
        for player in player_team:
            new = await init_hero(db, session, hero_id=player.id)
            new.name = player.name

            player_team_update.append(new)

        player_team = player_team_update

    else:
        hero = data.get('hero')
        hero = await init_hero(db, session, hero_id=hero.id)
        player_team = [hero]

    engine_data = {
        "enemy_team": enemy_team,
        "player_team": player_team,
        "exit_state": FortressState.map_nav,
        "exit_message": 'Вы победили и готовы к новым подвигам\n',
        "exit_kb": map_nav_inline(),
        "battle_type": 'fort',
        "is_inline": True,
    }

    config = message.bot.get('config')
    is_dev = config.tg_bot.is_dev

    factory = BattleFactory(enemy_team, player_team, LocationState.home, '', home_kb, is_dev)

    logger = factory.create_battle_logger()
    engine = factory.create_battle_engine()
    ui = factory.create_battle_interface(message, state, db, engine, logger)

    engine.initialize()
    ui.engine = engine
    ui.engine_data = engine_data

    await state.update_data(engine_data=engine_data)
    await state.update_data(engine=engine)
    await state.update_data(logger=logger)

    await ui.start_battle()


async def select_floor(cb: CallbackQuery, state: FSMContext):
    if cb.data == keyboard["back"]:
        await LocationState.town.set()
        await cb.message.delete()
        return await cb.message.answer(locale['town'], reply_markup=town_kb)

    data = await state.get_data()
    map: Map = data.get('map', MapFactory.create_map(6, 6))

    text = f'Приветствую путник в нашем форте!\n\n'
    text, kb = map_zone(map, text)

    await state.update_data(map=map)

    await FortressState.map_nav.set()
    await cb.message.edit_text(text, reply_markup=kb)


async def map_move(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    map: Map = data.get('map')

    map.move(cb.data)
    await state.update_data(map=map)

    text, kb = map_zone(map)

    await FortressState.map_nav.set()
    await cb.message.edit_text(text, reply_markup=kb)


async def map_action(cb: CallbackQuery, state: FSMContext):
    if cb.data == 'Выход':
        await cb.message.delete()
        return await to_home(cb.message)

    text = '⁢'
    kb = map_nav_inline()

    if cb.data == 'town':
        text = "Вы вошли в город %№;#@:"
        kb = fortress_town_inline
        await FortressState.town.set()

    if cb.data == 'battle':
        return await map_battle_init(cb.message, state)

    await cb.message.edit_text(text=text, reply_markup=kb)


async def town(cb: CallbackQuery, state: FSMContext):
    if cb.data == 'exit':
        return await to_map(cb, state)

    text = '⁢'
    kb = fortress_town_inline

    if cb.data == 'square':
        kb = fortress_town_inline
        text = "Огромная площадь города выглядит красиво, но когда на ней нет ни единой души, это вселяет некий страх."

    if cb.data == 'tavern':
        kb = fortress_town_inline
        text = "За стойкой стоит трактирщик и нервно потирая стакан, иногда бросает на вас беспокойный взгляд."

    await cb.message.edit_text(text, reply_markup=kb)


async def to_map(cb, state):
    data = await state.get_data()
    map: Map = data.get('map')

    text = 'Вы вышли из города\n\n'
    text, kb = map_zone(map, text)

    await FortressState.map_nav.set()
    return await cb.message.edit_text(text, reply_markup=map_nav_inline())


def map_zone(map, text_=''):
    zone = map.get_zone()

    text = text_
    text += map.display_map()
    text += f'\n\n'
    text += f'Дебаг: ({zone}, {map.current_coordinates}, {map.current_direction})'
    text += f'\n\n'

    kb = map_nav_inline()

    if zone == 'town':
        kb = map_nav_inline(is_town=True)
        text += "Вы можете войти в город:"

    if zone == 'forest':
        kb = map_nav_inline(is_battle=True)
        text += "Вы напасть на монстра:"

    return text, kb


async def map_battle_init(message: Message, state):
    db = DBCommands(message.bot.get('db'))
    session = message.bot.get('session')

    # 1. Получить ареал
    # 2. Получить монстров зоны
    # 2.1. Получить монстров ареала
    # 3. Сгенерировать противников
    # 3.1. Учесть сложность локации
    # 3.2. Учесть поведение противников ареала (Агрессивные, пассивные)
    # 3.2. Учесть плотность противников (Много ~= до 6, как обычно ~= 2-3, мало ~= 1-2 )

    enemy_id = 2

    enemy = await init_enemy(db, enemy_id, session)

    await state.update_data(enemy_team=[enemy])
    await battle_init(message, state)


map_navs = ['left', 'right', 'up']
map_actions = ['town', 'exit', 'explorer', 'battle']


def fortress(dp: Dispatcher):
    dp.register_callback_query_handler(select_floor, state=FortressState.select_floor)
    dp.register_callback_query_handler(map_move, lambda t: t.data in map_navs, state=FortressState.map_nav)
    dp.register_callback_query_handler(map_action, lambda t: t.data in map_actions, state=FortressState.map_nav)
    dp.register_callback_query_handler(town, state=FortressState.town)
