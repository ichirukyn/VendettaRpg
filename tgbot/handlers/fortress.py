from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from tgbot.handlers.battle.interface import BattleFactory
from tgbot.keyboards.inline import list_inline
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import town_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import FortressState
from tgbot.misc.state import LocationState
from tgbot.misc.state import TowerState
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
        "exit_state": LocationState.home,
        "exit_message": '',
        "exit_kb": home_kb,
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


async def battle_start(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.bot.get('db'))
    data = await state.get_data()

    floor_id = data.get('floor_id')

    if cb.data == keyboard["back"]:
        enemies = await floor_enemies(db, floor_id)
        kb = list_inline(enemies)

        await TowerState.select_enemy.set()
        return await cb.message.edit_text('Доступные противники:', reply_markup=kb)

    await battle_init(cb.message, state)


async def select_floor(cb: CallbackQuery, state: FSMContext):
    not cb.message.from_user.first_name

    if cb.data == keyboard["back"]:
        await LocationState.town.set()
        await cb.message.delete()
        return await cb.message.answer(locale['town'], reply_markup=town_kb)

    # db = DBCommands(cb.bot.get('db'))

    # floor_id = int(cb.data)
    # await state.update_data(floor_id=floor_id)

    # enemies = await floor_enemies(db, floor_id)
    # kb = list_inline(enemies)

    # await TowerState.select_enemy.set()
    # await cb.message.edit_text('Доступные противники:', reply_markup=kb)


async def floor_enemies(db, floor_id):
    enemies_list = []
    enemies = await db.get_arena_floor_enemies(floor_id)

    for enemy in enemies:
        if enemy['team_id'] is not None:
            team = await db.get_team(enemy['team_id'])
            enemies_list.append({'id': enemy['id'], 'name': team['name']})
        else:
            enemy = await db.get_enemy(enemy['id'])
            enemies_list.append(enemy)

    return enemies_list


def fortress(dp: Dispatcher):
    # dp.register_message_handler(battle_init, state='*')
    dp.register_callback_query_handler(select_floor, state=FortressState.select_floor)
    # dp.register_callback_query_handler(battle_start, state=BattleState.battle_start)
