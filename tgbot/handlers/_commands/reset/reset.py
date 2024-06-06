import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from tgbot.handlers._commands.start.auth import check_auth
from tgbot.models.user import DBCommands


# Сброс ОС в СО
async def reset_all(message: Message):
    db = DBCommands(message.bot.get('db'))
    dp = message.bot.get('dp')
    users = await db.get_users()

    for user in users:
        hero_id = await db.get_hero_id(user['id'])
        stats = await db.get_hero_stats(hero_id)
        lvl = await db.get_hero_lvl(hero_id)

        chat_id = user.get('chat_id')
        text = 'Вам сбросили характеристики, не забудьте /start, для избежания ошибок...'

        try:
            await dp.storage.update_data(chat=chat_id, hero=None)
            await message.bot.send_message(chat_id=chat_id, text=text, reply_markup=ReplyKeyboardRemove())
        except Exception:
            print(f'{chat_id} Не узнает о сбросе..')

        await reset_stats(db, hero_id, stats, lvl)
        await asyncio.sleep(1)

    await message.answer('Характеристики игроков сброшены')


async def reset_one(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    user = await db.get_user_id(message.from_user.id)

    hero_id = await db.get_hero_id(user.get('id'))
    stats = await db.get_hero_stats(hero_id)
    lvl = await db.get_hero_lvl(hero_id)

    await reset_stats(db, hero_id, stats, lvl)
    await message.answer('Ваши характеристики сброшены')

    await check_auth(message, state)


async def reset_stats(db, hero_id, stats, lvl):
    if stats['total_stats'] >= 8:
        await db.update_hero_stat('strength', 1, hero_id)
        await db.update_hero_stat('health', 1, hero_id)
        await db.update_hero_stat('speed', 1, hero_id)
        await db.update_hero_stat('dexterity', 1, hero_id)
        await db.update_hero_stat('accuracy', 1, hero_id)
        await db.update_hero_stat('soul', 1, hero_id)
        await db.update_hero_stat('intelligence', 1, hero_id)
        await db.update_hero_stat('submission', 1, hero_id)
        await db.update_hero_stat('total_stats', 8, hero_id)

    # new_so = stats['free_stats'] + stats['total_stats'] - 8
    new_so = (lvl.get('lvl') * 10) + 20
    await db.update_hero_stat('free_stats', new_so, hero_id)


def reset(dp):
    dp.register_message_handler(reset_one, commands=["reset"], state='*')
    dp.register_message_handler(reset_all, commands=["reset_all"], state='*')
