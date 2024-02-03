from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.handlers.tower import floor_enemies
from tgbot.keyboards.inline import list_inline
from tgbot.keyboards.reply import town_kb
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import BattleState
from tgbot.misc.state import CampusState
from tgbot.misc.state import LocationState
from tgbot.models.user import DBCommands


async def battle_start(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.bot.get('db'))
    data = await state.get_data()

    floor_id = data.get('floor_id')

    if cb.data == keyboard["back"]:
        enemies = await floor_enemies(db, floor_id)
        kb = list_inline(enemies)

        await CampusState.select_enemy.set()
        return await cb.message.edit_text('Доступные противники:', reply_markup=kb)

    # await battle_init(cb.message, state)


async def select_floor(cb: CallbackQuery, state: FSMContext):
    if cb.data == keyboard["back"]:
        await LocationState.town.set()
        await cb.message.delete()
        return await cb.message.answer(locale['town'], reply_markup=town_kb)

    db = DBCommands(cb.bot.get('db'))

    floor_id = int(cb.data)
    await state.update_data(floor_id=floor_id)

    enemies = await floor_enemies(db, floor_id)
    kb = list_inline(enemies)

    await CampusState.select_enemy.set()
    await cb.message.edit_text('Доступные противники:', reply_markup=kb)


def campus(dp: Dispatcher):
    # dp.register_message_handler(battle_init, commands=["battle"], state='*')
    dp.register_callback_query_handler(select_floor, state=CampusState.select_floor)
    dp.register_callback_query_handler(battle_start, state=BattleState.battle_start)
