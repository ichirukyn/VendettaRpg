from random import choice
from random import randint

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.handlers.battle.interface import BattleFactory
from tgbot.handlers.tower import floor_enemies
from tgbot.keyboards.inline import battle_start_inline
from tgbot.keyboards.inline import list_inline
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import town_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.hero import init_team
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import CampusState
from tgbot.misc.state import LocationState
from tgbot.models.entity.enemy import init_enemy
from tgbot.models.user import DBCommands


async def battle_init(cb: CallbackQuery, state: FSMContext, is_group=False):
    db = DBCommands(cb.message.bot.get('db'))
    dp = cb.message.bot.get('dp')

    session = cb.message.bot.get('session')
    data = await state.get_data()

    hero = data.get('hero')
    enemies = data.get('campus_enemies', [])
    enemies = list(filter(lambda x: x.get('enemy_id', None) is not None, enemies))

    hero = await init_hero(db, session, hero_id=hero.id, chat_id=hero.chat_id)

    player_team = [hero]
    enemy_team = []

    if hero.team_id is not None and is_group:
        if hero.team_id > 0 and hero.is_leader:
            team = await db.get_team_heroes(hero.team_id)
            player_team = await init_team(db, session, team, dp, hero)

    if not enemies:
        return await cb.message.edit_text('Ошибка, нет противников..')

    # Ввести умное увеличение противников
    range_ = len(player_team)
    print(f'Количество противников: {range_}')

    for i in range(range_ if range_ >= 1 else 1):
        # Ввести более умную выборку противников..
        rand_enemy = choice(enemies)
        id = rand_enemy.get('enemy_id')
        enemy = await init_enemy(db, int(id), session)

        print('enemy_TO', enemy.total_stats)
        enemy_team.append(enemy)

        hero_avg_lvl = sum(hero.lvl for hero in player_team)
        enemy_avg_lvl = sum(hero.lvl for hero in enemy_team)
        delta = hero_avg_lvl - enemy_avg_lvl

        print('delta', delta)
        if delta <= 0:
            delta = 0

        enemy.auto_distribute(delta)

        print('new_enemy_TO', enemy_team[0].total_stats)

    floors = await db.get_arena_floors()
    kb = list_inline(floors)

    engine_data = {
        "enemy_team": enemy_team,
        "player_team": player_team,
        "exit_state": CampusState.select_floor,
        "exit_message": '',
        "battle_type": 'campus',
        "exit_kb": kb,
        "is_inline": False,
    }

    config = cb.message.bot.get('config')
    is_dev = config.tg_bot.is_dev

    factory = BattleFactory(enemy_team, player_team, LocationState.home, '', home_kb, is_dev)

    logger = factory.create_battle_logger()
    engine = factory.create_battle_engine()
    ui = factory.create_battle_interface(cb.message, state, db, engine, logger)

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
        enemies_list, _ = await floor_enemies(db, floor_id)
        kb = list_inline(enemies_list)

        await CampusState.select_floor.set()
        return await cb.message.edit_text('Доступные противники:', reply_markup=kb)

    if cb.data == keyboard['battle_solo']:
        return await battle_init(cb, state)

    if cb.data == keyboard['battle_group']:
        return await battle_init(cb, state, True)


async def select_floor(cb: CallbackQuery, state: FSMContext):
    if cb.data == keyboard["back"]:
        await LocationState.town.set()
        await cb.message.delete()
        return await cb.message.answer(locale['town'], reply_markup=town_kb)

    data = await state.get_data()
    hero = data.get('hero')

    session = cb.bot.get('session')

    floor_id = int(cb.data)

    _, enemies = await floor_enemies(session, floor_id)

    await state.update_data(floor_id=floor_id)
    await state.update_data(campus_enemies=enemies)

    is_group = hero.team_id != 0
    kb = battle_start_inline(is_group)

    await CampusState.battle.set()
    await cb.message.edit_text('Вы уверены?', reply_markup=kb)


def campus(dp: Dispatcher):
    dp.register_callback_query_handler(select_floor, state=CampusState.select_floor)
    dp.register_callback_query_handler(battle_start, state=CampusState.battle)
