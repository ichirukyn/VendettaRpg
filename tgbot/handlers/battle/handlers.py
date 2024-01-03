from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.handlers.battle.interface import BattleFactory
from tgbot.misc.state import BattleState
from tgbot.models.user import DBCommands


async def battle_handler_init(message: Message, state: FSMContext, ):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    config = message.bot.get('config')
    is_dev = config.tg_bot.is_dev

    factory = BattleFactory(is_dev=is_dev, **engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    return ui


async def start_battle(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.start_battle()


async def user_turn(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_user_turn(message, state)


async def user_sub_turn(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_user_sub_turn(message, state)


async def select_technique(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_select_technique(message, state)


async def select_skill(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_select_skill(message, state)


async def select_skill_confirm(message: Message, state: FSMContext):
    ui = await battle_handler_init(message, state)
    await ui.process_select_skill_confirm(message, state)


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
    dp.register_message_handler(user_sub_turn, state=BattleState.user_sub_turn)
    dp.register_message_handler(select_technique, state=BattleState.select_technique)
    dp.register_message_handler(select_target, state=BattleState.select_target)
    dp.register_message_handler(select_skill, state=BattleState.select_skill)
    dp.register_message_handler(select_skill_confirm, state=BattleState.select_skill_confirm)
