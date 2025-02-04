from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from tgbot.api.arena import fetch_arena_enemies
from tgbot.api.enemy import fetch_enemy_team
from tgbot.handlers.battle.interface import BattleFactory
from tgbot.keyboards.inline import battle_start_inline
from tgbot.keyboards.inline import list_inline
from tgbot.keyboards.reply import town_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.hero import init_team
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.other import formatted
from tgbot.misc.state import BattleState
from tgbot.misc.state import LocationState
from tgbot.misc.state import TowerState
from tgbot.models.entity.enemy import init_enemy
from tgbot.models.user import DBCommands


async def battle_init(message: Message, state: FSMContext, is_group=False):
    db = DBCommands(message.bot.get('db'))
    dp = message.bot.get('dp')

    config = message.bot.get('config')
    is_dev = config.tg_bot.is_dev

    session = message.bot.get('session')
    data = await state.get_data()

    hero = data.get('hero')
    chat_id = data.get('hero_chat_id', None)

    hero = await init_hero(db, session, hero_id=hero.id, chat_id=chat_id)

    enemy_team = data.get('enemy_team', [])
    player_team = [hero]

    if hero.team_id is not None and is_group:
        if hero.team_id > 0 and hero.is_leader:
            team = await db.get_team_heroes(hero.team_id)
            player_team = await init_team(db, session, team, dp, hero)

    floors = await db.get_arena_floors()
    kb = list_inline(floors)

    # TODO: The Perry
    # pet = copy(enemy_team[0])
    # pet.techniques = hero.techniques
    # pet.name = "The Перри!"
    # player_team.append(pet)

    engine_data = {
        "enemy_team": enemy_team,
        "player_team": player_team,
        "exit_state": TowerState.select_floor,
        "exit_message": '',
        "battle_type": 'tower',
        "exit_kb": kb,
        "is_inline": False,
        "is_dev": is_dev,
    }

    factory = BattleFactory(**engine_data)

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
    session = cb.bot.get('session')
    data = await state.get_data()

    floor_id = data.get('floor_id')

    if cb.data == keyboard["back"]:
        enemies_list, _ = await floor_enemies(session, floor_id)
        kb = list_inline(enemies_list)

        await TowerState.select_enemy.set()
        return await cb.message.edit_text('Доступные противники:', reply_markup=kb)

    if cb.data == keyboard['battle_solo']:
        return await battle_init(cb.message, state)

    if cb.data == keyboard['battle_group']:
        return await battle_init(cb.message, state, True)


async def select_floor(cb: CallbackQuery, state: FSMContext):
    if cb.data == keyboard["back"]:
        await LocationState.town.set()
        await cb.message.delete()
        return await cb.message.answer(locale['town'], reply_markup=town_kb)

    session = cb.bot.get('session')

    floor_id = int(cb.data)
    await state.update_data(floor_id=floor_id)

    enemies_list, _ = await floor_enemies(session, floor_id)
    kb = list_inline(enemies_list)

    await TowerState.select_enemy.set()
    await cb.message.edit_text('Доступные противники:', reply_markup=kb)


async def select_enemy(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.bot.get('db'))
    session = cb.bot.get('session')
    data = await state.get_data()
    hero = data.get('hero')

    if cb.data == keyboard["back"]:
        floors = await db.get_arena_floors()
        kb = list_inline(floors)

        await TowerState.select_floor.set()
        return await cb.message.edit_text(locale['tower'], reply_markup=kb)

    enemy_team = []

    if 'enemy' in cb.data:
        id = cb.data.split('_')[1]

        if isinstance(id, str):
            enemy = await init_enemy(db, int(id), session)
            enemy_team.append(enemy)
    else:
        id = cb.data.split('_')[1]

        if isinstance(id, str):
            team_enemies = await fetch_enemy_team(session, id)

            for e in team_enemies:
                enemy = await init_enemy(db, e['enemy_id'], session)
                # enemy.name += f" \"{e['prefix']}\""
                enemy_team.append(enemy)

    if len(enemy_team) > 1:
        text = f"Выбраны противники:\n"
        for entity in enemy_team:
            entity.name += f" - {enemy_team.index(entity) + 1}"
            stats = f"{entity.name} — {formatted(entity.lvl)} Уровень\n"
            text += stats
    else:
        entity = enemy_team[0]
        name = f"{entity.name}"
        text = f"Выбран противник:\n`{name} — {formatted(entity.lvl)} Уровень`"

    await state.update_data(enemy_team=enemy_team)

    is_group = hero.team_id != 0
    kb = battle_start_inline(is_group)

    await BattleState.battle_start.set()
    await cb.message.edit_text(text, reply_markup=kb, parse_mode='Markdown')


async def floor_enemies(session, floor_id):
    enemies_list = []
    enemies = await fetch_arena_enemies(session, floor_id)

    for enemy in enemies:
        if enemy.get('enemy_id', None) is not None:
            id = f"enemy_{enemy.get('enemy_id')}"
            name = enemy.get('enemy').get('name', 'Моб:')
        else:
            id = f"team_{enemy.get('team_id')}"
            name = enemy.get('team').get('name', 'Команда:')

        enemies_list.append({
            'id': id,
            'name': name
        })

    return enemies_list, enemies


def tower(dp: Dispatcher):
    dp.register_message_handler(battle_init, commands=["battle"], state='*')
    dp.register_callback_query_handler(select_floor, state=TowerState.select_floor)
    dp.register_callback_query_handler(select_enemy, state=TowerState.select_enemy)
    dp.register_callback_query_handler(battle_start, state=BattleState.battle_start)
