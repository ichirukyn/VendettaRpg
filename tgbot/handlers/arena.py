from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.handlers.battle.interface import BattleFactory
from tgbot.handlers.location import to_home
from tgbot.keyboards.reply import arena_type_kb
from tgbot.keyboards.reply import home_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.hero import init_team
from tgbot.misc.hero import leader_on_team
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import ArenaState
from tgbot.misc.state import BattleState
from tgbot.misc.state import LocationState
from tgbot.models.entity.hero import Hero
from tgbot.models.user import DBCommands


async def arena_select_type(message: Message, state: FSMContext):
    if message.text == keyboard["back"]:
        await LocationState.arena.set()
        return await message.answer(locale['arena'], reply_markup=arena_type_kb)

    session = message.bot.get('session')
    db = DBCommands(message.bot.get('db'))
    dp = message.bot.get('dp')

    data = await state.get_data()
    hero = data['hero']
    pvp_type = data.get('pvp_type', None)
    chat_id = data.get('hero_chat_id', None)

    hero = await init_hero(db, session, hero_id=hero.id, chat_id=chat_id)

    try:
        text_solo = f'{hero.name} бросил вам вызов.'
        text_team = f'{hero.name}, бросил вызов вашей группе.'

        player_team = []
        enemy_team = []

        id = int(message.text)
        chat_id = hero.chat_id

        if id == hero.id:
            return await message.answer('Вызывать себя на бой, можно только в голове XD')

        if pvp_type == 'solo':
            try:
                player = await init_hero(db, session, hero_id=id)
                chat_id = player.chat_id
            except Exception:
                return await message.answer(locale['error_repeat'])

            enemy_team.append(player)
            player_team.append(hero)

            await state.update_data(player_team=player_team)
            await state.update_data(enemy_team=enemy_team)

            await message.bot.send_message(chat_id=player.chat_id, text=text_solo)

        if pvp_type == 'team':
            if hero.team_id != 0:
                team = await db.get_team_heroes(hero.team_id)
                player_team = await init_team(db, session, team)
            else:
                player_team = [hero]

            team_bd = await db.get_team_heroes(id)
            enemy_team = await init_team(db, session, team_bd)

            for enemy in enemy_team:
                if enemy.id == hero.id:
                    return await message.answer('Вызывать свою команду на бой, можно только в 1 на 1')

            await state.update_data(player_team=player_team)
            await state.update_data(enemy_team=enemy_team)

            leader = leader_on_team(enemy_team)
            chat_id = leader.chat_id

            await message.bot.send_message(chat_id=leader.chat_id, text=text_team)

        await dp.storage.update_data(chat=chat_id, player_team=player_team)
        await dp.storage.update_data(chat=chat_id, enemy_team=enemy_team)
        await dp.storage.update_data(chat=chat_id, pvp_hero=hero)
        await dp.storage.update_data(chat=chat_id, pvp_type=pvp_type)

        await message.answer('Вы бросили вызов')
    except TypeError as e:
        print(f'Arena Error\n{e}')


async def arena_battle(message: Message, state: FSMContext):
    data = await state.get_data()
    hero = data['hero']

    pvp_type = data.get('pvp_type', None)
    pvp_hero = data.get('pvp_hero', None)
    enemy_team = data.get('enemy_team', [])

    if pvp_hero is None:
        await message.answer('Вы потерялись на дороге жизни..')
        return to_home(message)

    text_solo = f'{hero.name} принял вызов {pvp_hero.name}.'
    text_team = f'{hero.name}, принял вызов {pvp_hero.name}, от лица группы.'

    if pvp_type == 'solo':
        await message.bot.send_message(chat_id=hero.chat_id, text=text_solo)
    if pvp_type == 'team':
        leader = leader_on_team(enemy_team)
        await message.bot.send_message(chat_id=leader.chat_id, text=text_team)

    await state.update_data(pvp_hero=None)
    return await arena_team_battle(message, state)


async def arena_pass(message: Message, state: FSMContext):
    data = await state.get_data()

    player_team = data.get('player_team')
    hero = data.get('hero')

    if player_team is not None:
        for player in player_team:
            if not isinstance(player, Hero):
                continue

            await message.bot.send_message(chat_id=player.chat_id, text=f'{hero.name} отказался от боя.')

    await state.update_data(pvp_hero=None)

    await LocationState.arena.set()
    return await message.answer('Вы отказались от боя.', reply_markup=arena_type_kb)


async def arena_team_battle(message: Message, state: FSMContext):
    data = await state.get_data()

    player_team = data.get('player_team', [])
    enemy_team = data.get('enemy_team', [])
    pvp_type = data.get('pvp_type', None)

    db = DBCommands(message.bot.get('db'))
    dp = message.bot.get('dp')

    config = message.bot.get('config')
    is_dev = config.tg_bot.is_dev

    factory = BattleFactory(enemy_team, player_team, LocationState.home, '', home_kb, is_dev)

    engine = factory.create_battle_engine()
    logger = factory.create_battle_logger()
    ui = factory.create_battle_interface(message, state, db, engine, logger)

    engine.initialize()
    ui.engine = engine

    if pvp_type == 'solo':
        battle_type = 'arena_one'
    else:
        battle_type = 'arena_team'

    engine_data = {
        "enemy_team": enemy_team,
        "player_team": player_team,
        "exit_state": LocationState.home,
        "exit_message": '',
        "exit_kb": home_kb,
        "battle_type": battle_type,
        "is_inline": False,
    }

    for e in engine.order:
        if not isinstance(e, Hero):
            continue

        if e.chat_id != 0:
            if pvp_type == 'solo':
                e.statistic.count_team_to_team += 1
            else:
                e.statistic.count_one_to_one += 1

            await dp.storage.update_data(chat=e.chat_id, engine_data=engine_data)
            await dp.storage.update_data(chat=e.chat_id, engine=engine)
            await dp.storage.update_data(chat=e.chat_id, logger=logger)
            await dp.storage.set_state(chat=e.chat_id, state=BattleState.load)

    return await ui.start_battle()


def arena(dp: Dispatcher):
    dp.register_message_handler(
        arena_battle, lambda t: t.text == keyboard['battle_start'], state=ArenaState.select_type
    )
    dp.register_message_handler(arena_pass, lambda t: t.text == keyboard['pass'], state=ArenaState.select_type)
    dp.register_message_handler(arena_select_type, state=ArenaState.select_type)
    dp.register_message_handler(arena_team_battle, state=ArenaState.team_battle)
