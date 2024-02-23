from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from tgbot.api.hero import create_hero
from tgbot.api.race import fetch_race
from tgbot.api.race import fetch_race_classes
from tgbot.api.user import create_user
from tgbot.api.user import get_user
from tgbot.api.user import get_user_hero
from tgbot.handlers.location import to_home
from tgbot.keyboards.reply import confirm_kb
from tgbot.keyboards.reply import entry_kb
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import list_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.logger import logger
from tgbot.misc.state import BattleState
from tgbot.misc.state import LocationState
from tgbot.misc.state import RegState
from tgbot.models.entity._class import class_init
from tgbot.models.entity.hero import HeroFactory
from tgbot.models.entity.race import race_init
from tgbot.models.user import DBCommands


async def register_user(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    session = message.bot.get('session')

    data = await state.get_data()
    hero = data.get('hero')

    hero.name = message.text
    logger.info('Register | name:', hero.name)

    data = await state.get_data()

    chat_id = message.from_user.id
    race_id = data.get('select_race', 1)
    class_id = data.get('select_class', 1)

    logger.debug('Register | chat_id:', chat_id)
    logger.debug('Register | race_id:', race_id)
    logger.debug('Register | class_id:', class_id)

    user = await get_user(session, chat_id)
    if user.get('id') is not None:
        await message.answer('Вы уже зарегистрированы')
        return to_home(message)

    try:
        user_data = await create_user({'chat_id': chat_id, 'login': message.from_user.first_name, 'ref_id': 1})
        user_id = user_data.get('id')
        logger.info('Register | user_id:', user_id)

        hero_data = await create_hero({'user_id': user_id, 'name': hero.name, 'race_id': race_id, 'class_id': class_id})
        hero.id = hero_data.get('id', 0)
        logger.info('Register | hero.id:', hero.id)

        if hero.id == 0:
            logger.error('Register | hero.id == 0')

        await db.add_hero_stats(hero.id, hero)
        await db.add_hero_lvl(hero.id, 1, 0)
        await db.add_hero_weapon(hero.id, 1)

        await db.add_hero_technique(hero.id, 1)
        # await db.add_hero_skill(hero_id, 1)

        # await db.add_trader_hero(hero_id, 3, 1, 1)
        # await db.add_trader_hero(hero_id, 4, 1, 1)

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
    # TODO: Проверить race_name, ничего ли не сломалось
    for race in races:
        if race['name'] == race_name:
            await state.update_data(select_race=race['id'])

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

    data = await state.get_data()
    race_id = data.get('select_race')

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


async def entry_point(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    config = message.bot.get('config')
    session = message.bot.get('session')

    if message.chat.id not in config.tg_bot.admin_ids and config.tg_bot.is_dev:
        await BattleState.load.set()
        return await message.answer('Доступ пока только для админов..', reply_markup=ReplyKeyboardRemove())

    chat_id = message.chat.id
    print('chat_id: ', chat_id)

    user = await get_user(session, chat_id)

    # if user.get('is_baned', False):
    #     return await message.answer('Вас забанили Т.Т')

    try:
        if user is None:
            races = await fetch_race(session)
            kb = list_kb(races, is_back=False)

            hero = HeroFactory.create_init_hero(0, chat_id, message.from_user.first_name)
            await state.update_data(hero=hero)

            await RegState.select_race.set()
            return await message.answer('Выбери стартовую расу:', reply_markup=kb)

        else:
            hero_data = await get_user_hero(session, user.get('id'))

            if hero_data is None:
                text = 'Ошибка получения героя, звоните Ichiru..'
                return await message.answer(text, reply_markup=ReplyKeyboardRemove())

            hero = await init_hero(db, session, hero_data=hero_data)
            print(f"hero_id: {hero.id}")

            await state.update_data(hero=hero)
            await state.update_data(hero_id=hero.id)

            print('-- Exit on /start -- \n')
            await LocationState.home.set()
            return await message.answer(f'Приветствую тебя, {hero.name}!', reply_markup=home_kb, parse_mode='Markdown')
    except Exception as e:
        await message.answer(f'Ошибка..\n {e}', reply_markup=ReplyKeyboardRemove())


async def started(message: Message):
    db = DBCommands(message.bot.get('db'))

    users = await db.get_users()

    for user in users:
        await message.bot.send_message(chat_id=user['chat_id'],
                                       text="Бот запущен, напишите /start, для перехода на главный экран..")
        # await asyncio.sleep(1)


# Сброс ОС в СО
async def reset_all(message: Message):
    db = DBCommands(message.bot.get('db'))

    users = await db.get_users()

    for user in users:
        hero_id = await db.get_hero_id(user['id'])
        stats = await db.get_hero_stats(hero_id)
        lvl = await db.get_hero_lvl(hero_id)

        await reset(db, hero_id, stats, lvl)

    await message.answer('Характеристики игроков сброшены')


async def reset_one(message: Message):
    db = DBCommands(message.bot.get('db'))
    user = await db.get_user_id(message.from_user.id)

    hero_id = await db.get_hero_id(user.get('id'))
    stats = await db.get_hero_stats(hero_id)
    lvl = await db.get_hero_lvl(hero_id)

    await reset(db, hero_id, stats, lvl)
    await message.answer('Ваши характеристики сброшены')


async def reset(db, hero_id, stats, lvl):
    if stats['total_stats'] > 8:
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


async def deactivate(message: Message):
    bot = message.bot.get('db')

    db = DBCommands(message.bot.get('db'))
    users = await db.get_users()

    for user in users:
        try:
            await bot.send_message(user.get('chat_id'), "Бот будет отключен через несколько минут.")
        except Exception:
            pass


def start(dp: Dispatcher):
    dp.register_message_handler(started, commands=["started"], state='*')
    dp.register_message_handler(reset_one, commands=["reset"], state='*')
    dp.register_message_handler(reset_all, commands=["reset_all"], state='*')
    dp.register_message_handler(deactivate, commands=["deactivate"], state='*')
    dp.register_message_handler(entry_point, commands=["start"], state='*')
    dp.register_message_handler(entry_point, state=RegState.entry)
    dp.register_message_handler(register_user, state=RegState.user_name)
    dp.register_message_handler(select_race, state=RegState.select_race)
    dp.register_message_handler(select_class, state=RegState.select_class)
    dp.register_message_handler(select_class_confirm, state=RegState.select_class_confirm)
