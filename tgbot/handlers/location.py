from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from tgbot.api.technique import fetch_technique
from tgbot.handlers.team import to_team_main
from tgbot.keyboards.inline import list_inline
from tgbot.keyboards.inline import shop_buy_inline
from tgbot.keyboards.inline import top_inline
from tgbot.keyboards.reply import arena_type_kb
from tgbot.keyboards.reply import back_kb
from tgbot.keyboards.reply import battle_start_kb
from tgbot.keyboards.reply import character_distribution_kb
from tgbot.keyboards.reply import character_info_kb
from tgbot.keyboards.reply import character_kb
from tgbot.keyboards.reply import equip_kb
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import inventory_kb
from tgbot.keyboards.reply import team_accept_kb
from tgbot.keyboards.reply import town_kb
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.other import formatted
from tgbot.misc.state import ArenaState
from tgbot.misc.state import CampusState
from tgbot.misc.state import CharacterState
from tgbot.misc.state import FortressState
from tgbot.misc.state import LocationState
from tgbot.misc.state import ShopState
from tgbot.misc.state import TeamState
from tgbot.misc.state import TowerState
from tgbot.misc.utils import check_before_send
from tgbot.models.entity.hero import HeroInfo
from tgbot.models.user import DBCommands


async def location_main_select(message: Message, state: FSMContext):
    if message.text == keyboard['location']:
        await LocationState.town.set()
        return await message.answer(locale['town'], reply_markup=town_kb)

    elif message.text == keyboard['character']:
        await location_character(message, state)

    elif message.text == keyboard['top']:
        await LocationState.top.set()
        await message.answer('⁢', reply_markup=ReplyKeyboardRemove())
        await message.answer(locale['top'], reply_markup=top_inline)


async def location_town(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.text == keyboard['tower']:
        return await location_tower(message, state)

    if message.text == keyboard['fortress']:
        return await location_fortress(message, state)

    if message.text == keyboard['campus']:
        return await location_campus(message, state)

    if message.text == keyboard['arena']:
        pvp_hero = data.get('pvp_hero', None)

        if pvp_hero is not None:
            await ArenaState.select_type.set()
            return await message.answer('Принять вызов?', reply_markup=battle_start_kb)

        await LocationState.arena.set()
        await message.answer(locale['arena'], reply_markup=arena_type_kb)

    if message.text == keyboard['team']:
        invite_team_id = data.get('invite_team_id')
        if invite_team_id is not None:
            await TeamState.accept_invite.set()
            return await message.answer(locale['team_accept'], reply_markup=team_accept_kb)

        send_invite_to_team = data.get('send_invite_to_team')
        if send_invite_to_team is not None:
            await TeamState.accept_leader.set()
            return await message.answer('Вы хотите принять нового участника?', reply_markup=team_accept_kb)

        await to_team_main(message, state)

    if message.text == keyboard['training']:
        await message.answer('В разработке...\nПланируется манекен, которого можно будет пинать, для теста урона')

    if message.text == keyboard['shop']:
        db = DBCommands(message.bot.get('db'))
        items = await db.get_trader_items(1)

        kb = list_inline(items)

        await LocationState.store.set()
        await message.answer('⁢', reply_markup=ReplyKeyboardRemove())
        return await message.answer(locale['shop'], reply_markup=kb)

    if message.text == keyboard["back"]:
        return await to_home(message)


async def location_arena(message: Message, state: FSMContext):
    if message.text == keyboard["back"]:
        await LocationState.town.set()
        return await message.answer(locale['town'], reply_markup=town_kb)

    if message.text == keyboard['battle_group']:
        await state.update_data(pvp_type='team')
        await ArenaState.select_type.set()
        return await message.answer(f'Введите ID команды:', reply_markup=back_kb)

    if message.text == keyboard['battle_solo']:
        await state.update_data(pvp_type='solo')
        await ArenaState.select_type.set()
        return await message.answer(f'Введите ID игрока:', reply_markup=back_kb)


async def location_team(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.message.bot.get('db'))
    data = await state.get_data()

    if cb.data == keyboard["back"]:
        await LocationState.town.set()
        await cb.message.delete()
        return await cb.message.answer(locale['town'], reply_markup=town_kb)

    if cb.data == 'Создать команду':
        await TeamState.add_name.set()
        await cb.message.delete()
        await cb.message.answer('Введите название команды:', reply_markup=back_kb)

    if cb.data == 'Все команды':
        teams = await db.get_teams()
        kb = list_inline(teams, cb_data='team_id')

        await TeamState.team_list.set()
        await cb.message.edit_text('Список команд.\n (Нажмите, чтобы отправить заявку)', reply_markup=kb)

    if cb.data == 'Добавить игрока':
        await TeamState.send_invite.set()
        await cb.message.delete()
        await cb.message.answer('Введите ID игрока:', reply_markup=back_kb)

    if cb.data == 'Исключить игрока':
        pass

    if cb.data == 'Список участников':
        hero = data.get('hero')
        team = await db.get_team_heroes(hero.team_id)

        kb = list_inline(team, 2, cb_data='hero_id')
        await TeamState.teammate_list.set()
        await cb.message.edit_text('Список участников:', reply_markup=kb)

    if cb.data == 'Выйти из группы':
        pass

    if cb.data == 'Настройки':
        pass


async def location_tower(message: Message, state: FSMContext):
    print('Arena Floors')

    db = DBCommands(message.bot.get('db'))
    floors = await db.get_arena_floors()

    kb = list_inline(floors)

    await TowerState.select_floor.set()
    await message.answer('⁢', reply_markup=ReplyKeyboardRemove())
    await message.answer(locale['tower'], reply_markup=kb)


async def location_fortress(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    floors = await db.get_arena_floors()

    kb = list_inline(floors)

    await FortressState.select_floor.set()
    await message.answer('⁢', reply_markup=ReplyKeyboardRemove())
    await message.answer(locale['tower'], reply_markup=kb)


async def location_campus(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    floors = await db.get_arena_floors()

    kb = list_inline(floors)

    await CampusState.select_floor.set()
    await message.answer('⁢', reply_markup=ReplyKeyboardRemove())
    await message.answer(locale['campus'], reply_markup=kb)


async def location_character(message: Message, state: FSMContext):
    if message.text == keyboard['distribution']:
        await CharacterState.distribution_menu.set()
        await message.answer(locale['distribution_tip'], parse_mode='Markdown')
        return await message.answer(locale['distribution'], reply_markup=character_distribution_kb)

    if message.text == keyboard["back"]:
        await LocationState.home.set()
        return await message.answer(locale['home'], reply_markup=home_kb)

    if message.text == keyboard['equipment']:
        await CharacterState.equip.set()
        return await message.answer(locale['equip'], reply_markup=equip_kb)

    if message.text == keyboard['inventory']:
        await CharacterState.inventory.set()
        return await message.answer(locale['inventory'], reply_markup=inventory_kb)

    if message.text == keyboard['techniques']:
        session = message.bot.get('session')

        data = await state.get_data()
        hero = data['hero']

        techniques = await fetch_technique(session, hero.race.id, hero._class.id)
        kb = list_inline(techniques)

        await CharacterState.techniques.set()
        await message.answer('⁢', reply_markup=ReplyKeyboardRemove())
        return await message.answer(locale['techniques_select'], reply_markup=kb)

    data = await state.get_data()
    hero = data.get('hero')

    if message.text == keyboard['info']:
        await CharacterState.info_menu.set()
        return await message.answer(hero.info.status_all(hero), reply_markup=character_info_kb,
                                    parse_mode='Markdown')
    info = HeroInfo()
    await LocationState.character.set()
    await message.answer(info.status(hero), reply_markup=character_kb(hero.free_stats), parse_mode='Markdown')


async def location_store(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    hero_id = data['hero_id']

    if cb.data == keyboard["back"]:
        await cb.message.delete()
        return await to_town(cb.message)

    item_id = int(cb.data)

    db = DBCommands(cb.message.bot.get('db'))
    items = await db.get_trader_items()

    hero_items = await db.get_hero_trader_items(hero_id)

    # Если есть у пользователя и количество 0, то выкинуть на главную..
    for hero_item in hero_items:
        if item_id == int(hero_item['item_id']):
            if hero_item['item_count'] <= 0:
                kb = list_inline(items)

                text = f"{locale['shop']}\n\nВы скупили все предметы данного типа.."

                await LocationState.store.set()

                if cb.message.text != text:
                    await cb.message.edit_text(text, reply_markup=kb)

                return

    for item in items:
        if item_id == int(item['item_id']):
            await state.update_data(item_id=item['item_id'])
            await state.update_data(item_count=item['item_count'])

            text = f"*{item['name']}*\n{item['desc']}\n\n" \
                   f"Цена: {formatted(item['price'])}\n" \
                   f"Введите количество: (доступно {item['item_count']})"

            await ShopState.buy.set()

            if cb.message.text != text:
                await cb.message.edit_text(text, reply_markup=shop_buy_inline)


async def location_top(cb: CallbackQuery, state: FSMContext):
    if cb.data == keyboard["back"]:
        await cb.message.delete()
        return await to_home(cb.message)

    data = await state.get_data()
    _hero = data.get('hero')

    db = DBCommands(cb.message.bot.get('db'))

    heroes = await db.get_all_heroes_stats(cb.data)

    top = [f'Топ игроков:']
    hero_data = ''
    hero_top = 0

    i = 0

    for hero in heroes:
        if hero.get('hero_id', 0) == _hero.id:
            hero_data = f"{i + 1}. 👤 *{hero['name']} — {formatted(hero[cb.data])}*"
            hero_top = i
            top.append(hero_data)
        else:
            top.append(f"{i + 1}. {hero['name']} — {formatted(hero[cb.data])}")

        i += 1

    top_ten = top[:11]
    top_ten[1] = f"🥇{top_ten[1][2:]}"
    top_ten[2] = f"🥈{top_ten[2][2:]}"
    top_ten[3] = f"🥉{top_ten[3][2:]}"

    if hero_top >= 10:
        top_ten.append('...')
        top_ten.append(hero_data)

    text = '\n'.join(top_ten)

    # Сбрасывает top, потому что функция не умеет это делать сама
    top = []
    return await check_before_send(cb, text, top_inline)


async def to_home(message):
    await LocationState.home.set()
    await message.answer(locale['home'], reply_markup=home_kb)


async def to_town(message):
    await LocationState.town.set()
    await message.answer(locale['town'], reply_markup=town_kb)


def location(dp: Dispatcher):
    dp.register_message_handler(to_home, commands=["to_home"], state='*')

    dp.register_message_handler(location_main_select, state=LocationState.home)
    dp.register_message_handler(location_character, state=LocationState.character)
    dp.register_callback_query_handler(location_store, state=LocationState.store)
    dp.register_callback_query_handler(location_top, state=LocationState.top)

    dp.register_message_handler(location_town, state=LocationState.town)
    dp.register_message_handler(location_arena, state=LocationState.arena)
    dp.register_message_handler(location_tower, state=LocationState.tower)
    dp.register_message_handler(location_fortress, state=LocationState.fortress)
    dp.register_callback_query_handler(location_team, state=LocationState.team)
