from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message

from tgbot.keyboards.reply import home_kb
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import LocationState
from tgbot.misc.state import SettingsState
from tgbot.models.settings import Settings
from tgbot.models.settings import setting_list


async def settings_keyboard(message: Message, state: FSMContext):
    data = await state.get_data()
    settings_ = data.get('settings')
    settings_inline = InlineKeyboardMarkup(row_width=1)

    for setting in setting_list:
        name = f"{setting.get('label', '')}"
        attr = setting.get('attr', '')
        value = getattr(settings_, attr)

        if hasattr(settings_, attr) and getattr(settings_, attr):
            name = f"✅ {name}"
        else:
            name = f"☑️ {name}"

        settings_inline.add(InlineKeyboardButton(text=name.format(value), callback_data=attr))

    settings_inline.add(InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]))

    return settings_inline


async def settings_menu(message: Message, state: FSMContext, text=''):
    await SettingsState.setting.set()

    if text is None or text == '':
        text = locale['settings']

    settings_inline = await settings_keyboard(message, state)

    return await message.answer(text=text, reply_markup=settings_inline)


async def setting_toggle(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    settings_: Settings = data.get('settings')
    value = ''

    if cb.data == keyboard['back']:
        await cb.message.delete()

        await LocationState.home.set()
        return await cb.message.answer(locale['home'], reply_markup=home_kb)

    if cb.data == 'all':
        if settings_.all:
            settings_.deactivate_all()
        else:
            settings_.active_all()
    else:
        value = settings_.filter(cb.data)

    text = ''

    for setting in setting_list:
        setting_name = setting.get('label', 'Настройка')
        setting_value = setting.get('attr', '')

        if setting_value == cb.data:
            text = f"Вы изменили {setting_name.format(value)}\n{locale['settings']}"

    await state.update_data(settings=settings_)

    settings_inline = await settings_keyboard(cb.message, state)
    return await cb.message.edit_text(text, reply_markup=settings_inline)


def settings(dp: Dispatcher):
    dp.register_message_handler(settings_menu, state=LocationState.settings)
    dp.register_callback_query_handler(setting_toggle, state=SettingsState.setting)
