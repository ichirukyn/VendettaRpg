from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import list_inline, battle_start_inline
from tgbot.keyboards.reply import home_kb, town_kb
from tgbot.misc.battle import BattleFactory
from tgbot.misc.hero import init_hero
from tgbot.misc.locale import locale
from tgbot.misc.other import formatted
from tgbot.misc.state import BattleState, LocationState, TowerState
from tgbot.models.entity.enemy import init_enemy
from tgbot.models.user import DBCommands


async def battle_init(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()

    enemy_team = data.get('enemy_team')
    player_team = data.get('player_team')

    if player_team:
        player_team_update = []
        for player in player_team:
            new = await init_hero(db, player.id)
            new.name = player.name

            player_team_update.append(new)

        player_team = player_team_update

    else:
        hero = data.get('hero')
        player_team = [hero]

    factory = BattleFactory(enemy_team, player_team, LocationState.home, '', home_kb)

    logger = factory.create_battle_logger()
    engine = factory.create_battle_engine()
    ui = factory.create_battle_interface(message, state, db, engine, logger)

    engine.initialize()
    ui.engine = engine

    engine_data = {
        "enemy_team": enemy_team,
        "player_team": player_team,
        "exit_state": LocationState.home,
        "exit_message": '',
        "exit_kb": home_kb,
    }

    await state.update_data(engine_data=engine_data)
    await state.update_data(engine=engine)
    await state.update_data(logger=logger)

    await ui.start_battle()


async def battle_start(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.bot.get('db'))
    data = await state.get_data()

    floor_id = data.get('floor_id')

    if cb.data == '🔙 Назад':
        enemies = await floor_enemies(db, floor_id)
        kb = list_inline(enemies)

        await TowerState.select_enemy.set()
        return await cb.message.edit_text('Доступные противники:', reply_markup=kb)

    await battle_init(cb.message, state)


async def select_floor(cb: CallbackQuery, state: FSMContext):
    if cb.data == '🔙 Назад':
        await LocationState.town.set()
        await cb.message.delete()
        return await cb.message.answer(locale['town'], reply_markup=town_kb)

    db = DBCommands(cb.bot.get('db'))

    floor_id = int(cb.data)
    await state.update_data(floor_id=floor_id)

    enemies = await floor_enemies(db, floor_id)
    kb = list_inline(enemies)

    await TowerState.select_enemy.set()
    await cb.message.edit_text('Доступные противники:', reply_markup=kb, parse_mode='MarkdownV2')


async def select_enemy(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.bot.get('db'))
    data = await state.get_data()

    floor_id = data.get('floor_id')

    if cb.data == '🔙 Назад':
        floors = await db.get_arena_floors()
        kb = list_inline(floors)

        await TowerState.select_floor.set()
        return await cb.message.edit_text(locale['tower'], reply_markup=kb)

    enemies = await db.get_arena_floor_enemies(floor_id)

    enemy_id = None
    team_id = None

    for e in enemies:
        if e['id'] == int(cb.data):
            enemy_id = e['enemy_id']
            team_id = e['team_id']

    enemy_team = []

    if enemy_id is not None:
        enemy = await init_enemy(db, enemy_id)
        enemy_team.append(enemy)

    elif team_id is not None:
        team_id = await db.get_enemy_team_id(team_id)
        for entity in team_id:
            enemy = await init_enemy(db, entity['enemy_id'])
            enemy.name += f" \"{entity['prefix']}\""
            enemy_team.append(enemy)
    else:
        print('Противник не найден...')

    if len(enemy_team) > 1:
        text = f"Выбраны противники:\n"
        for entity in enemy_team:
            stats = f"{entity.name} — {formatted(entity.total_stats)} ОС\n"
            text += stats
    else:
        entity = enemy_team[0]
        name = f"{entity.name} {entity.race_name}"
        text = f"Выбран противник: {name} — {formatted(entity.lvl)} ОС"

    await state.update_data(enemy_team=enemy_team)

    await BattleState.battle_start.set()
    await cb.message.edit_text(text, reply_markup=battle_start_inline, parse_mode='MarkdownV2')


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


def tower(dp: Dispatcher):
    dp.register_message_handler(battle_init, commands=["battle"], state='*')
    dp.register_callback_query_handler(select_floor, state=TowerState.select_floor)
    dp.register_callback_query_handler(select_enemy, state=TowerState.select_enemy)
    dp.register_callback_query_handler(battle_start, state=BattleState.battle_start)
