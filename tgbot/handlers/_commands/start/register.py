import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from logger import logger
from tgbot.api.hero import create_hero
from tgbot.api.race import fetch_race
from tgbot.api.race import fetch_race_classes
from tgbot.api.user import create_user
from tgbot.api.user import get_user
from tgbot.handlers.location import to_home
from tgbot.keyboards.reply import confirm_kb
from tgbot.keyboards.reply import entry_kb
from tgbot.keyboards.reply import list_kb
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import RegState
from tgbot.models.entity._class import class_init
from tgbot.models.entity.race import race_init
from tgbot.models.user import DBCommands


async def register_user(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    session = message.bot.get('session')

    data = await state.get_data()
    hero = data.get('hero')

    # Регулярное выражение для ника
    pattern = re.compile(r'^[a-zA-Zа-яА-Я0-9]+$')

    if 3 >= len(message.text) >= 25:
        return await message.answer('Ник игрока должен состоять от 5 до 25 символов')

    if not pattern.match(message.text):
        return await message.answer('Ник игрока содержит недопустимые символы.')

    hero.name = message.text
    print('Register | name:', hero.name)

    data = await state.get_data()

    chat_id = message.from_user.id
    race_id = data.get('select_race', 1)
    class_id = data.get('select_class', 1)

    logger.debug(f'Register | chat_id: {chat_id}')
    logger.debug(f'Register | race_id: {race_id}')
    logger.debug(f'Register | class_id: {class_id}')

    # user = await get_user(session, chat_id)
    # if user is not None:
    #     await message.answer('Вы уже зарегистрированы')
    #     return to_home(message)

    try:
        user_data = await create_user({'chat_id': f"{chat_id}", 'login': message.from_user.first_name, 'ref_id': 1})
        user_id = user_data.get('id')
        print('Register | user_id:', user_id)

        if user_id is None:
            return logger.warning("Register | user create error")

        hero_data = await create_hero({'user_id': user_id, 'name': hero.name, 'race_id': race_id, 'class_id': class_id})
        hero.id = hero_data.get('id')

        if hero.id is None:
            return logger.warning("Register | hero create error")

        print('Register | hero.id:', hero.id)

        await db.add_hero_stats(hero.id, hero)
        await db.add_hero_lvl(hero.id, 1, 0)
        await db.add_hero_weapon(hero.id, 1)

        await db.add_hero_technique(hero.id, 1)
        # await db.add_hero_skill(hero_id, 1)

        await state.update_data(hero=hero)
        await state.update_data(hero_id=hero.id)
        logger.info('Register | success')

        await RegState.entry.set()
        await message.answer(f"Добро пожаловать в мир Vendetta, {hero.name}!", reply_markup=entry_kb)
    except Exception as e:
        logger.error('Register | error')
        logger.error(e)
        text = f"Произошла ошибка! Напишите @Ichirukyn, разберёмся..\nОшибка:{e}"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())


async def select_race(message: Message, state: FSMContext):
    session = message.bot.get('session')

    data = await state.get_data()
    hero = data.get('hero')

    race_name = message.text
    races = await fetch_race(session)

    for race in races:
        if race.get('name', '') == race_name:
            await state.update_data(select_race=race.get('id', 0))

            race = await race_init(session, race)
            hero.race = race
            hero.race.apply(hero)

            text = hero.info.character_info(hero, 'race')
            text += '\nТеперь выберите стартовый класс:'

            classes = await fetch_race_classes(session, race.id)
            kb = list_kb(classes)

            await RegState.select_class.set()
            await message.answer(text, reply_markup=kb)


async def select_class(message: Message, state: FSMContext):
    session = message.bot.get('session')

    data = await state.get_data()
    hero = data.get('hero')

    if message.text == keyboard["back"]:
        races = await fetch_race(session)
        kb = list_kb(races, is_back=False)

        await RegState.select_race.set()
        return await message.answer('Выбери стартовую расу:', reply_markup=kb)

    race_id = data.get('select_race')

    if race_id is None or race_id == 0:
        print('race_id', race_id)
        await RegState.entry.set()
        return await message.answer('Произошла ошибка, начните сначала:', reply_markup=entry_kb)


    class_name = message.text
    classes_bd = await fetch_race_classes(session, race_id)

    for _class in classes_bd:
        if _class['name'] == class_name:
            await state.update_data(select_class=_class['id'])

            _class = await class_init(session, _class)
            hero._class = _class
            hero._class.apply(hero)

            text = hero.info.character_info(hero, 'class')
            text += '\n\nВы уверены в своём выборе?'

            await RegState.select_class_confirm.set()
            await message.answer(text, reply_markup=confirm_kb)


async def select_class_confirm(message: Message, state: FSMContext):
    session = message.bot.get('session')

    data = await state.get_data()
    race_id = data.get('select_race')

    if message.text == keyboard["back"]:
        classes = await fetch_race_classes(session, race_id)
        kb = list_kb(classes)

        await RegState.select_class.set()
        return await message.answer('Выберите стартовый класс:', reply_markup=kb)
    if message.text == keyboard['yes']:
        await RegState.user_name.set()
        return await message.answer(locale['register'], reply_markup=ReplyKeyboardRemove())


def register(dp: Dispatcher):
    dp.register_message_handler(register_user, state=RegState.user_name)
    dp.register_message_handler(select_race, state=RegState.select_race)
    dp.register_message_handler(select_class, state=RegState.select_class)
    dp.register_message_handler(select_class_confirm, state=RegState.select_class_confirm)
