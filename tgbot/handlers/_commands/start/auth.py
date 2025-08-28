import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from logger import logger
from tgbot.api.hero import get_hero
from tgbot.api.race import fetch_race
from tgbot.api.user import get_user
from tgbot.api.user import get_user_hero
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import list_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.state import LocationState
from tgbot.misc.state import RegState
from tgbot.models.entity.hero import HeroFactory
from tgbot.models.settings import Settings
from tgbot.models.user import DBCommands


async def check_auth(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        settings = data.get('settings')

        db = DBCommands(message.bot.get('db'))

        config = message.bot.get('config')
        session = message.bot.get('session')

        # if message.chat.id not in config.tg_bot.admin_ids and config.tg_bot.is_dev:
        #     return

        chat_id = message.chat.id
        logger.info(f'chat_id: {chat_id}')

        user = await get_user(session, chat_id)

        if user is None:
            races = await fetch_race(session)
            kb = list_kb(races, is_back=False)

            hero = HeroFactory.create_init_hero(0, chat_id, message.from_user.first_name)
            await state.update_data(hero=hero)

            await RegState.select_race.set()
            return await message.answer('Выбери стартовую расу:', reply_markup=kb)

        if user.get('is_baned', False):
            return await message.answer('Вас забанили Т.Т')

        hero_data = await get_user_hero(session, user.get('id'))

        # Вход под кем-то
        if message.chat.id in config.tg_bot.admin_ids and len(message.text.split(' ')) == 2:
            hero_id = message.text.split(' ')[1]
            hero = await get_hero(session, int(hero_id))

            if hero_id and hero.get('id'):
                hero_data = hero
                hero_data['chat_id'] = message.chat.id
                await state.update_data(hero_chat_id=message.chat.id)

        if hero_data is None:
            text = 'Ошибка получения героя'
            return await message.answer(text, reply_markup=ReplyKeyboardRemove())

        hero = await init_hero(db, session, hero_data.get('id'), hero_data.get('chat_id', None))
        # print(f"hero_id: {hero.id}")

        if settings is None:
            settings = Settings()

        await state.update_data(hero=hero)
        await state.update_data(hero_id=hero.id)
        await state.update_data(settings=settings)

        print('-- Exit on /start -- \n')
        await LocationState.home.set()
        return await message.answer(f'Приветствую тебя, {hero.name}!', reply_markup=home_kb, parse_mode='Markdown')
        # await test_init_hero(session, db)

    except Exception as e:
        await message.answer(f'Неизвестная ошибка\n {e}', reply_markup=ReplyKeyboardRemove())


async def test_init_hero(session, db):
    hero_data = await get_user_hero(session, 6)

    hero_data_list = [hero_data for _ in range(100)]
    batch_size = 1  # Количество пользователей, запускаемых одновременно
    durations = []

    for i in range(0, len(hero_data_list), batch_size):
        batch = hero_data_list[i:i + batch_size]
        tasks = [init_hero(db, session, hero_data['id']) for hero_data in batch]
        results = await asyncio.gather(*tasks)
        durations.extend([result[1] for result in results])

    total = sum(durations)
    average = total / len(durations)
    max_time = max(durations)

    print(f'Total time: {total:.2f} seconds')
    print(f'Average time: {average:.2f} seconds')
    print(f'Max time: {max_time:.2f} seconds')


def auth(dp):
    dp.register_message_handler(check_auth, commands=["start"], state='*')
    dp.register_message_handler(check_auth, state=RegState.entry)
