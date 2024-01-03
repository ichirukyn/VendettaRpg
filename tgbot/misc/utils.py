import random
import re

from aiogram.types import CallbackQuery


async def check_before_send(cb: CallbackQuery, text, kb):
    text = re.sub(r'[\*_`\[\]\(\)]', '', text)

    if cb.message.text != text:
        return await cb.message.edit_text(text, reply_markup=kb)


def spread(value, _range=0.2):
    _spread = value * _range
    # return round(random.uniform(value - _spread, value + _spread))
    return round(value * (random.randint(85, 100) / 100))
