from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from tgbot.api.hero import create_hero_spell
from tgbot.api.hero import create_hero_technique
from tgbot.api.hero import delete_hero_spell
from tgbot.api.hero import delete_hero_technique
from tgbot.api.hero import get_hero_spell
from tgbot.api.hero import get_hero_technique
from tgbot.api.spells import fetch_spell
from tgbot.api.spells import get_spell
from tgbot.api.technique import fetch_technique
from tgbot.api.technique import get_technique
from tgbot.handlers import lib_stats
from tgbot.keyboards.inline import back_inline
from tgbot.keyboards.inline import list_inline
from tgbot.keyboards.inline import skill_add_inline
from tgbot.keyboards.inline import skill_del_inline
from tgbot.keyboards.reply import back_kb
from tgbot.keyboards.reply import character_distribution_kb
from tgbot.keyboards.reply import character_info_kb
from tgbot.keyboards.reply import character_kb
from tgbot.keyboards.reply import inventory_kb
from tgbot.misc.Inventory import BookItem, PotionItem
from tgbot.misc.Inventory import ConsumableItem
from tgbot.misc.Inventory import Item
from tgbot.misc.Inventory import WeaponItem
from tgbot.misc.hero import init_hero
from tgbot.misc.hero import update_hero_weapon
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import CharacterState
from tgbot.misc.state import LocationState
from tgbot.models.entity.spells import spell_init
from tgbot.models.entity.techniques import technique_init
from tgbot.models.user import DBCommands

inventory = {
    keyboard['weapon']: 'weapon',
    keyboard['quest']: 'quest',
    keyboard['potion']: 'potion',
    keyboard['technique_book']: 'technique_book',
    keyboard['other']: 'other',
}


async def distribution_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    hero = data['hero']

    if message.text == keyboard["back"] or hero.free_stats <= 0:
        await LocationState.character.set()

        return await message.answer(hero.info.status(hero), reply_markup=character_kb(hero.free_stats))

    stat = lib_stats.get(message.text)

    if stat:
        hero.__getattribute__(stat)
        await state.update_data(train_stat=stat)

        await CharacterState.distribution.set()
        return await message.answer(f"Доступно {hero.free_stats} СО\nВведите количество:", reply_markup=back_kb)


async def distribution(message: Message, state: FSMContext):
    if message.text == keyboard["back"]:
        await CharacterState.distribution_menu.set()
        return await message.answer(locale['distribution'], reply_markup=character_distribution_kb)

    db = DBCommands(message.bot.get('db'))
    session = message.bot.get('session')

    data = await state.get_data()
    hero = data['hero']
    hero_id = data['hero_id']
    stat = data['train_stat']
    chat_id = data.get('hero_chat_id', None)
    flat_stat = f"flat_{stat}"

    try:
        count = int(message.text)
    except ValueError:
        return await message.answer("Введите корректное число")

    if 0 < count <= hero.free_stats:
        stat_value = hero.__getattribute__(flat_stat) + count
        hero.__setattr__(flat_stat, stat_value)

        hero.total_stats_flat += count
        hero.free_stats -= count

        await db.update_hero_stat(stat, stat_value, hero_id)
        await db.update_hero_stat('free_stats', hero.free_stats, hero_id)
        await db.update_hero_stat('total_stats', hero.total_stats_flat, hero_id)

        hero = await init_hero(db, session, hero.id, chat_id=chat_id)

        await state.update_data(hero=hero)

        if hero.free_stats <= 0:
            await LocationState.character.set()
            return await message.answer(hero.info.status(hero), reply_markup=character_kb(hero.free_stats))
        else:
            await CharacterState.distribution_menu.set()
            await message.answer(locale['distribution'], reply_markup=character_distribution_kb)

    else:
        await message.answer(f"Доступно {hero.free_stats} СО\nВведите количество:", reply_markup=back_kb)


async def character_techniques(cb: CallbackQuery, state: FSMContext):
    session = cb.message.bot.get('session')

    data = await state.get_data()
    hero = data['hero']

    if cb.data == keyboard["back"]:
        await cb.message.delete()
        await LocationState.character.set()

        return await cb.message.answer(hero.info.status(hero), reply_markup=character_kb(hero.free_stats))

    technique_id = int(cb.data)

    hero_technique = await get_hero_technique(session, hero.id, technique_id)
    res = await get_technique(session, technique_id)

    kb = skill_add_inline
    fix = 'Не закреплён'

    if hero_technique is not None:
        kb = skill_del_inline
        fix = 'Закреплён'

    await state.update_data(technique_fix=technique_id)

    if res is not None:
        technique = technique_init(res)

        text = (
            f"{technique.info(hero)}\n"
            f"{fix}"
        )
    else:
        text = locale['error_repeat']

    await CharacterState.technique_fix.set()
    await cb.message.edit_text(text, reply_markup=kb)


async def character_technique_fix(cb: CallbackQuery, state: FSMContext):
    session = cb.message.bot.get('session')

    data = await state.get_data()
    hero = data['hero']
    technique_id = data['technique_fix']

    if cb.data == keyboard['back']:
        skills = await fetch_technique(session, hero.race.id, hero._class.id)
        kb = list_inline(skills)

        await CharacterState.techniques.set()
        return await cb.message.edit_text(locale['techniques_select'], reply_markup=kb)

    if technique_id == 1 and cb.data == 'Открепить':
        return await cb.message.edit_text('Открепить эту технику нельзя..', reply_markup=back_inline)

    if cb.data == 'Прикрепить':
        data = {'hero_id': hero.id, 'technique_id': technique_id}
        await create_hero_technique(data, hero.id)

    if cb.data == 'Открепить':
        await delete_hero_technique(session, hero.id, technique_id)

    skills = await fetch_technique(session, hero.race.id, hero._class.id)
    kb = list_inline(skills)

    await CharacterState.techniques.set()
    await cb.message.edit_text(locale['techniques_select'], reply_markup=kb)


async def character_spell(cb: CallbackQuery, state: FSMContext):
    session = cb.message.bot.get('session')

    data = await state.get_data()
    hero = data['hero']

    if cb.data == keyboard["back"]:
        await cb.message.delete()
        await LocationState.character.set()

        return await cb.message.answer(hero.info.status(hero), reply_markup=character_kb(hero.free_stats))

    spell_id = int(cb.data)

    hero_spell = await get_hero_spell(session, hero.id, spell_id)
    res = await get_spell(session, spell_id)

    kb = skill_add_inline
    fix = 'Не закреплён'

    if hero_spell is not None:
        kb = skill_del_inline
        fix = 'Закреплён'

    await state.update_data(spell_fix=spell_id)

    if res is not None:
        spell = spell_init(res)

        text = (
            f"{spell.info(hero)}\n"
            f"{fix}"
        )
    else:
        text = locale['error_repeat']

    await CharacterState.spell_fix.set()
    await cb.message.edit_text(text, reply_markup=kb)


async def character_spell_fix(cb: CallbackQuery, state: FSMContext):
    session = cb.message.bot.get('session')

    data = await state.get_data()
    hero = data['hero']
    spell_id = data['spell_fix']

    if cb.data == keyboard['back']:
        spell = await fetch_spell(session)
        kb = list_inline(spell)

        await CharacterState.spells.set()
        return await cb.message.edit_text(locale['spells_select'], reply_markup=kb)

    if spell_id == 1 and cb.data == 'Открепить':
        return await cb.message.edit_text('Открепить эту технику нельзя..', reply_markup=back_inline)

    if cb.data == 'Прикрепить':
        data = {'hero_id': hero.id, 'spell_id': spell_id, 'lvl': 1}
        await create_hero_spell(data, hero.id)

    if cb.data == 'Открепить':
        await delete_hero_spell(session, hero.id, spell_id)

    spell = await fetch_spell(session)
    kb = list_inline(spell)

    await CharacterState.spells.set()
    await cb.message.edit_text(locale['spells_select'], reply_markup=kb)


async def character_equip(message: Message, state: FSMContext):
    data = await state.get_data()
    hero = data['hero']

    if message.text == 'Текущее оружие':
        await message.answer(hero.info.equip_stat(hero))

    if message.text == 'Артефакты (В разработке)':
        pass

    if message.text == keyboard["back"]:
        await LocationState.character.set()
        await message.answer(hero.info.status(hero), reply_markup=character_kb(hero.free_stats))


async def character_inventory(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))

    data = await state.get_data()
    hero = data['hero']

    if message.text == keyboard["back"]:
        await message.delete()
        await LocationState.character.set()

        return await message.answer(hero.info.status(hero), reply_markup=character_kb(hero.free_stats))

    if message.text not in inventory:
        return

    type = inventory.get(message.text)
    await state.update_data(inventory=type)

    items = await db.get_hero_inventory(type, hero.id)

    kb = list_inline(items)

    await CharacterState.inventory_items.set()
    await message.answer('⁢', reply_markup=ReplyKeyboardRemove())
    await message.answer(locale['inventory'], reply_markup=kb)


async def character_inventory_items(cb: CallbackQuery, state: FSMContext):
    if cb.data == keyboard["back"]:
        await cb.message.delete()

        await CharacterState.inventory.set()
        return await cb.message.answer(locale['inventory'], reply_markup=inventory_kb)

    db = DBCommands(cb.message.bot.get('db'))

    data = await state.get_data()
    type = data['inventory']
    hero = data['hero']

    item_id = int(cb.data)

    items = await db.get_hero_inventory(type, hero.id)

    for item in items:
        if item['item_id'] == item_id:
            i = Item(item)

            match type:
                case 'weapon':
                    i = WeaponItem(item)
                    await i.check(db, hero.id)
                case 'technique_book', 'spell_book':
                    i = BookItem(item)
                case 'potion':
                    i = PotionItem(item)
                    # await i.check(db, hero.id)
                case _:
                    i = ConsumableItem(item)

            text = i.get_desc()
            kb = i.get_kb()

            await state.update_data(inventory_item=item_id)

            await CharacterState.inventory_action.set()
            await cb.message.edit_text(text, reply_markup=kb)


async def character_inventory_action(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.message.bot.get('db'))

    data = await state.get_data()
    hero = data['hero']
    item_id = data['inventory_item']
    type = data['inventory']

    match cb.data:
        case 'Экипировать':
            await db.update_hero_weapon(hero.id, item_id, 0)
        case 'Снять':
            await db.update_hero_weapon(hero.id, item_id, 0)
        case 'Закрепить':
            # TODO: Подключить зельки к слотам
            pass

    hero = await update_hero_weapon(db, hero)

    items = await db.get_hero_inventory(type, hero.id)
    kb = list_inline(items)

    await state.update_data(hero=hero)

    await CharacterState.inventory_items.set()
    return await cb.message.edit_text(locale['inventory'], reply_markup=kb)


async def character_info_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    hero = data['hero']

    if message.text == 'Статус':
        return await message.answer(hero.info.status(hero), reply_markup=character_info_kb)

    if message.text == 'Статистика':
        return await message.answer(hero.statistic.get_statistic(), reply_markup=character_info_kb)

    if message.text == 'Полный статус':
        return await message.answer(hero.info.status_all(hero), reply_markup=character_info_kb)

    if message.text == 'Чистый статус':
        return await message.answer(hero.info.status_flat(hero), reply_markup=character_info_kb)

    if message.text == 'Раса':
        return await message.answer(hero.info.character_info(hero, 'race'), reply_markup=character_info_kb)

    if message.text == 'Класс':
        return await message.answer(hero.info.character_info(hero, 'class'), reply_markup=character_info_kb)

    if message.text == keyboard["back"]:
        await LocationState.character.set()
        return await message.answer(hero.info.status(hero), reply_markup=character_kb(hero.free_stats))


def character(dp: Dispatcher):
    dp.register_message_handler(distribution, state=CharacterState.distribution)
    dp.register_message_handler(distribution_menu, state=CharacterState.distribution_menu)
    dp.register_message_handler(character_equip, state=CharacterState.equip)
    dp.register_message_handler(character_inventory, state=CharacterState.inventory)
    dp.register_callback_query_handler(character_inventory_items, state=CharacterState.inventory_items)
    dp.register_callback_query_handler(character_inventory_action, state=CharacterState.inventory_action)
    dp.register_callback_query_handler(character_techniques, state=CharacterState.techniques)
    dp.register_callback_query_handler(character_technique_fix, state=CharacterState.technique_fix)
    dp.register_callback_query_handler(character_spell, state=CharacterState.spells)
    dp.register_callback_query_handler(character_spell_fix, state=CharacterState.spell_fix)

    dp.register_message_handler(character_info_menu, state=CharacterState.info_menu)
