from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.handlers.battle.interface import BattleFactory
from tgbot.keyboards.reply import home_kb
from tgbot.misc.state import BattleState
from tgbot.misc.state import LocationState
from tgbot.models.user import DBCommands


# Ошибка замедления работы бота
async def battle_handler_init(message: Message, state: FSMContext, ):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    config = message.bot.get('config')
    is_dev = config.tg_bot.is_dev

    if engine_data is None:
        engine_data = {
            "enemy_team": [data.get('hero')],
            "player_team": [],
            "exit_state": LocationState.home,
            "exit_message": 'Была ошибка...\n',
            "exit_kb": home_kb,
            "battle_type": 'battle',
            "is_inline": False,
        }

    factory = BattleFactory(is_dev=is_dev, **engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    return ui


async def start_battle(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.start_battle()


async def user_escape(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_user_escape_confirm(message, state)


async def user_pass_confirm(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_user_pass_confirm(message, state)


async def user_turn(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_user_turn(message, state)


async def user_sub_turn(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_user_sub_turn(message, state)


async def select_technique(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_select_technique(message, state)


async def select_technique_confirm(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_select_technique_confirm(message, state)


async def select_spell(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_select_spell(message, state)


async def select_spell_confirm(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_select_spell_confirm(message, state)


async def select_target(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_select_target(message, state)


async def revival(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_revival(message, state)


def battle(dp):
    dp.register_message_handler(start_battle, state=BattleState.battle)
    dp.register_message_handler(revival, state=BattleState.revival)
    dp.register_message_handler(user_turn, state=BattleState.user_turn)
    dp.register_message_handler(user_escape, state=BattleState.user_escape_confirm)
    dp.register_message_handler(user_pass_confirm, state=BattleState.user_pass_confirm)
    dp.register_message_handler(user_sub_turn, state=BattleState.user_sub_turn)
    dp.register_message_handler(select_technique, state=BattleState.select_technique)
    dp.register_message_handler(select_technique_confirm, state=BattleState.select_technique_confirm)
    dp.register_message_handler(select_target, state=BattleState.select_target)
    dp.register_message_handler(select_spell, state=BattleState.select_spell)
    dp.register_message_handler(select_spell_confirm, state=BattleState.select_spell_confirm)
