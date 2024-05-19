from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.keyboards.reply import admin_kb, admin_hero_stats_kb, back_kb, admin_update_kb
from tgbot.misc.locale import keyboard
from tgbot.misc.state import AdminState
from tgbot.models.user import DBCommands

stats = {
    'Сила': 'strength',
    'Контроль': 'control',
    'Скорость': 'speed',
    'Здоровье': 'health',
    'Свободные очки': 'free_stats',
    'Очки охоты': 'hunt_stats',
}


async def admin_start(message: Message):
    await AdminState.main.set()
    await message.answer("Админ панель v0.0.0:", reply_markup=admin_kb)


async def admin_main(message: Message, state: FSMContext):
    if message.text == 'Изменить характеристику':
        await state.update_data(admin_action='hero_stat')

        await AdminState.hero_stats.set()
        await message.answer('Выберите характеристику:', reply_markup=admin_hero_stats_kb)


async def admin_hero_id(message: Message, state: FSMContext):
    if message.text == keyboard["back"]:
        await AdminState.main.set()
        return await message.answer('Админ панель v0.0.0:', reply_markup=back_kb)

    try:
        id = int(message.text)
    except TypeError:
        return await message.answer('Введите корректное значение..')

    await state.update_data(admin_hero_id=id)
    await AdminState.value.set()
    await message.answer('Введи значение:', reply_markup=back_kb)


async def admin_hero_stats(message: Message, state: FSMContext):
    if message.text == keyboard["back"]:
        await AdminState.main.set()
        return await message.answer('Админ панель v0.0.0:', reply_markup=back_kb)

    if stats.get(message.text):
        stat = stats.get(message.text)
        await state.update_data(admin_action_value=stat)

        await AdminState.hero_id.set()
        await message.answer('Введите id игрока:', reply_markup=back_kb)
    else:
        await message.answer('(Нажми на кнопку)')


async def admin_value(message: Message, state: FSMContext):
    if message.text == keyboard["back"]:
        await AdminState.hero_id.set()
        return await message.answer('Введите id игрока:', reply_markup=back_kb)

    try:
        value = int(message.text)
    except TypeError:
        return await message.answer('Введите корректное значение..')

    await state.update_data(admin_value=value)
    await AdminState.bd_set.set()
    await message.answer('Обновляю данные?', reply_markup=admin_update_kb)


async def admin_bd_set(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await AdminState.main.set()
        return await message.answer('Админ панель v0.0.0:', reply_markup=back_kb)

    db = DBCommands(message.bot.get('db'))

    data = await state.get_data()

    action = data.get('admin_action')
    action_value = data.get('admin_action_value')
    value = data.get('admin_value')
    hero_id = data.get('admin_hero_id')

    if action == 'hero_stat':
        await db.update_hero_stat(action_value, value, hero_id)

    await AdminState.main.set()
    await message.answer('Готово!', reply_markup=admin_kb)


def register_admin(dp: Dispatcher, ):
    dp.register_message_handler(admin_start, commands=["admin"], state="*", is_admin=True)
    dp.register_message_handler(admin_main, state=AdminState.main)
    dp.register_message_handler(admin_hero_id, state=AdminState.hero_id)
    dp.register_message_handler(admin_hero_stats, state=AdminState.hero_stats)
    dp.register_message_handler(admin_value, state=AdminState.value)
    dp.register_message_handler(admin_bd_set, state=AdminState.bd_set)
