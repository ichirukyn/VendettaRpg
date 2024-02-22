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
from tgbot.keyboards.reply import confirm_kb
from tgbot.keyboards.reply import entry_kb
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import list_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import BattleState
from tgbot.misc.state import LocationState
from tgbot.misc.state import RegState
from tgbot.models.entity.hero import HeroFactory
from tgbot.models.user import DBCommands


async def register_user(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    session = message.bot.get('session')

    name = message.text

    data = await state.get_data()

    chat_id = message.from_user.id
    race_id = data.get('select_race', 1)
    class_id = data.get('select_class', 1)

    try:
        user_data = await create_user({'chat_id': chat_id, 'login': message.from_user.first_name, 'ref_id': 1})
        user_id = user_data.get('id')

        hero = HeroFactory.create_init_hero(user_id, chat_id, name)

        hero_data = await create_hero({'user_id': user_id, 'name': hero.name, 'race_id': race_id, 'class_id': class_id})
        hero.id = hero_data['id']

        await db.add_hero_stats(hero.id, hero)
        await db.add_hero_lvl(hero.id, 1, 0)
        await db.add_hero_weapon(hero.id, 1)

        # TODO: Добавить новые техники с привязкой к классу , стопорится тут, из-за пустой БД
        await db.add_hero_technique(hero.id, 1)
        # await db.add_hero_skill(hero_id, 1)

        # await db.add_trader_hero(hero_id, 3, 1, 1)
        # await db.add_trader_hero(hero_id, 4, 1, 1)

        await state.update_data(hero=hero)
        await state.update_data(hero_id=hero.id)

        await RegState.entry.set()
        await message.answer(f"Добро пожаловать в мир Vendetta, {name}!", reply_markup=entry_kb)
    except Exception as e:
        text = f"Произошла ошибка! Напишите @Ichirukyn, разберёмся..\nОшибка:{e}"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())


async def select_race(message: Message, state: FSMContext):
    session = message.bot.get('session')

    race_name = message.text
    races = await fetch_race(session)
    # TODO: Проверить race_name, ничего ли не сломалось
    for race in races:
        if race['name'] == race_name:
            await state.update_data(select_race=race['id'])
            text = race['desc']
            text += '\n\nТеперь выберите стартовый класс:'

            classes = await fetch_race_classes(session, race['id'])
            kb = list_kb(classes)

            await RegState.select_class.set()
            await message.answer(text, reply_markup=kb)


async def select_class(message: Message, state: FSMContext):
    session = message.bot.get('session')

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

            text = _class['desc']
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

    # try:
    if user is None:
        races = await fetch_race(session)
        kb = list_kb(races, is_back=False)

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
    # except Exception as e:
    #     await message.answer(f'Ошибка..\n {e}', reply_markup=ReplyKeyboardRemove())


async def started(message: Message):
    db = DBCommands(message.bot.get('db'))

    users = await db.get_users()

    for user in users:
        await message.bot.send_message(chat_id=user['chat_id'],
                                       text="Бот запущен, напишите /start, для перехода на главный экран..")
        # await asyncio.sleep(1)


# Сброс ОС в СО
async def change_os_to_so(message: Message):
    db = DBCommands(message.bot.get('db'))

    users = await db.get_users()

    for user in users:
        hero_id = await db.get_hero_id(user['id'])
        stats = await db.get_hero_stats(hero_id)

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

            new_so = stats['free_stats'] + stats['total_stats'] - 8
            await db.update_hero_stat('free_stats', new_so, hero_id)


async def deactivate(message: Message, state: FSMContext):
    data = await state.get_data()
    hero = data.get('hero')

    attr = []

    print('До')
    for effect in hero.active_bonuses[1].effects:
        print(f"{effect.name} - {effect.value} ({hero.__getattribute__(effect.attribute)})")
        attr.append(effect.attribute)

    print('')
    # hero.active_bonuses[1].deactivate()

    print('')
    print('После')
    for a in attr:
        print(f"{a} - {hero.__getattribute__(a)}")


def start(dp: Dispatcher):
    dp.register_message_handler(started, commands=["started"])
    dp.register_message_handler(deactivate, commands=["deactivate"], state='*')
    dp.register_message_handler(entry_point, commands=["start"], state='*')
    dp.register_message_handler(entry_point, state=RegState.entry)
    dp.register_message_handler(register_user, state=RegState.user_name)
    dp.register_message_handler(select_race, state=RegState.select_race)
    dp.register_message_handler(select_class, state=RegState.select_class)
    dp.register_message_handler(select_class_confirm, state=RegState.select_class_confirm)
