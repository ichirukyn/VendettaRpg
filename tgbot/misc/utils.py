from aiogram.types import CallbackQuery


async def check_before_send(cb: CallbackQuery, text, kb, parse='HTML'):
    if cb.message.text != text:
        return await cb.message.edit_text(text, reply_markup=kb, parse_mode=parse)
