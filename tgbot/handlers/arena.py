from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.keyboards.reply import arena_type_kb, home_kb
from tgbot.misc.battle import BattleFactory
from tgbot.misc.hero import init_hero, init_team, leader_on_team
from tgbot.misc.locale import locale
from tgbot.misc.state import ArenaState, LocationState
from tgbot.models.user import DBCommands


async def arena_select_type(message: Message, state: FSMContext):
    if message.text == '🔙 Назад':
        await LocationState.arena.set()
        return await message.answer(locale['arena'], reply_markup=arena_type_kb)

    db = DBCommands(message.bot.get('db'))
    dp = message.bot.get('dp')

    data = await state.get_data()
    hero = data['hero']
    pvp_type = data['pvp_type']

    try:
        if message.text == 'В бой':
            pvp_hero = data['pvp_hero']
            text_solo = f'{hero.name} принял вызов.'
            text_team = f'{hero.name}, принял вызов, от лица группы.'

            id = pvp_hero.id
        else:
            text_solo = f'{hero.name} бросил вам вызов.'
            text_team = f'{hero.name}, бросил вызов вашей группе.'

            id = int(message.text)

        if pvp_type == 'solo':
            player_team = []
            enemy_team = []

            player = await init_hero(db, hero_id=id)

            enemy_team.append(player)
            player_team.append(hero)

            await state.update_data(player_team=player_team)
            await state.update_data(enemy_team=enemy_team)

            await dp.storage.update_data(chat=player.chat_id, pvp_hero=hero)
            await dp.storage.update_data(chat=player.chat_id, pvp_type=pvp_type)
            await message.bot.send_message(chat_id=player.chat_id, text=text_solo)

        if pvp_type == 'team':
            team = await db.get_team_heroes(hero.team_id)
            player_team = await init_team(db, team)

            team_bd = await db.get_team_heroes(id)
            enemy_team = await init_team(db, team_bd)

            await state.update_data(player_team=player_team)
            await state.update_data(enemy_team=enemy_team)

            leader = leader_on_team(enemy_team)

            await dp.storage.update_data(chat=leader.chat_id, pvp_hero=hero)
            await dp.storage.update_data(chat=leader.chat_id, pvp_type=pvp_type)
            await message.bot.send_message(chat_id=leader.chat_id, text=text_team)

    except TypeError:
        print('Arena Error')

    if message.text == 'В бой':
        return await arena_team_battle(message, state)


async def arena_team_battle(message: Message, state: FSMContext):
    data = await state.get_data()

    player_team = data['player_team']
    enemy_team = data['enemy_team']

    db = DBCommands(message.bot.get('db'))
    dp = message.bot.get('dp')

    factory = BattleFactory(enemy_team, player_team, LocationState.home, '', home_kb)

    engine = factory.create_battle_engine()
    logger = factory.create_battle_logger()
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

    for e in engine.order:
        if e.chat_id != 0:
            await dp.storage.update_data(chat=e.chat_id, engine_data=engine_data)
            await dp.storage.update_data(chat=e.chat_id, engine=engine)
            await dp.storage.update_data(chat=e.chat_id, logger=logger)

    return await ui.start_battle()


def arena(dp: Dispatcher):
    dp.register_message_handler(arena_select_type, state=ArenaState.select_type)
    dp.register_message_handler(arena_team_battle, state=ArenaState.team_battle)
