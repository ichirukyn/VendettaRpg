from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from tgbot.api.race import fetch_race
from tgbot.api.user import get_user
from tgbot.keyboards.reply import confirm_kb
from tgbot.keyboards.reply import entry_kb
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import list_kb
from tgbot.misc.hero import init_hero
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import LocationState
from tgbot.misc.state import RegState
from tgbot.models.entity.hero import HeroFactory
from tgbot.models.user import DBCommands


async def register_user(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))

    # clans = await db.get_clans()
    # clan_name = clans[randint(0, len(clans) - 1)]

    name = message.text

    data = await state.get_data()
    race_id = data.get('select_race')
    class_id = data.get('select_class')

    chat_id = message.from_user.id
    login = message.from_user.first_name

    # ref_id = message.get_args  # TODO: Сделать рефку

    user_id = await db.add_user(chat_id, login, True, ref_id=1)
    if user_id is not None:
        hero = HeroFactory.create_init_hero(user_id, chat_id, name)

        hero_id = await db.add_hero(user_id, hero.name, race_id, class_id)
        hero.id = hero_id

        await db.add_hero_stats(hero_id, hero)
        await db.add_hero_lvl(hero_id, 1, 0)
        await db.add_hero_weapon(hero_id, 1)
        await db.add_hero_technique(hero_id, 1)  # TODO: Добавить новые техники с привязкой к классу

        # TODO: Переименовать в "поддержка", и переписать на взаимодействие со своей группой
        # await db.add_hero_skill(hero_id, 1)

        # await db.add_trader_hero(hero_id, 3, 1, 1)
        # await db.add_trader_hero(hero_id, 4, 1, 1)

        await state.update_data(hero=hero)
        await state.update_data(hero_id=hero_id)

        await RegState.entry.set()
        await message.answer(f"Добро пожаловать в мир Vendetta, {name}!", reply_markup=entry_kb)
    else:
        await message.answer("Произошла ошибка! Напишите @Ichirukyn, разберёмся..")


async def select_race(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))

    race_name = message.text
    race_bd = await db.get_races()
    # TODO: Проверить race_name, ничего ли не сломалось
    for race in race_bd:
        if race['name'] == race_name:
            await state.update_data(select_race=race['id'])
            text = race['desc']
            text += '\n\nТеперь выберите стартовый класс:'

            classes = await db.get_race_classes(race['id'])
            kb = list_kb(classes)

            await RegState.select_class.set()
            await message.answer(text, reply_markup=kb)


async def select_class(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))

    if message.text == keyboard["back"]:
        races = await db.get_races()
        kb = list_kb(races, is_back=False)

        await RegState.select_race.set()
        return await message.answer('Выбери стартовую расу:', reply_markup=kb)

    data = await state.get_data()
    race_id = data.get('select_race')

    class_name = message.text
    classes_bd = await db.get_race_classes(race_id)

    for _class in classes_bd:
        if _class['name'] == class_name:
            await state.update_data(select_class=_class['id'])

            text = _class['desc']
            text += '\n\nВы уверены в своём выборе?'

            await RegState.select_class_confirm.set()
            await message.answer(text, reply_markup=confirm_kb)


async def select_class_confirm(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))

    data = await state.get_data()
    race_id = data.get('select_race')

    if message.text == keyboard["back"]:
        classes = await db.get_race_classes(race_id)
        kb = list_kb(classes)

        await RegState.select_class.set()
        return await message.answer('Выберите стартовый класс:', reply_markup=kb)

    await RegState.user_name.set()
    return await message.answer(locale['register'], reply_markup=ReplyKeyboardRemove())


async def entry_point(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))

    chat_id = message.chat.id
    print('chat_id: ', chat_id)

    user = get_user(chat_id)
    print(user.json['login'])

    if user is None:
        races = fetch_race()
        # TODO: Проверить регистрацию
        kb = list_kb(races, is_back=False)

        await RegState.select_race.set()
        return await message.answer('Выбери стартовую расу:', reply_markup=kb)

    else:
        hero = await init_hero(db, user_id=user.json['id'])
        print(f"hero_id: {hero.id}")

        await state.update_data(hero=hero)
        await state.update_data(hero_id=hero.id)

        print('-- Exit on /start -- \n')
        await LocationState.home.set()
        return await message.answer(f'Приветствую тебя, {hero.name}!', reply_markup=home_kb, parse_mode='Markdown')


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
