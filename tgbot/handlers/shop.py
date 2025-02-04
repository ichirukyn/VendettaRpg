from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.keyboards.inline import list_inline, shop_buy_inline
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import ShopState, LocationState
from tgbot.misc.utils import check_before_send
from tgbot.models.user import DBCommands


async def buy_item(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.message.bot.get('db'))
    data = await state.get_data()

    hero = data['hero']
    item_id = data['item_id']
    item = await db.get_trader_item(item_id)

    if cb.data == keyboard["back"]:
        items = await db.get_trader_items()
        kb = list_inline(items)

        await LocationState.store.set()
        return await cb.message.edit_text(locale['shop'], reply_markup=kb)

    text = "Вам не хватает денег.."

    count = 1

    try:
        # match cb.data:
        #     case f"{keyboard['buy_all']}":
        #         count = item['item_count']

        if cb.data == keyboard["buy_one"]:
            count = 1
        elif cb.data == keyboard["buy_ten"]:
            count = 10
        elif cb.data == keyboard["buy_all"]:
            count = item['item_count']
    except ValueError:
        return await check_before_send(cb, "Введите корректное число", shop_buy_inline)

    if count > item['item_count']:
        return await check_before_send(cb, "Введите корректное число", shop_buy_inline)

    price = count * item['price']

    if price > hero.money:
        return await check_before_send(cb, "Вам не хватает денег..", shop_buy_inline)

    # TODO: Переделать под trader_id, сейчас только под 1 магазин..
    trader_items = await db.get_hero_trader_items(hero.id)
    is_trader_count = None

    for i in trader_items:
        if i['item_id'] == item_id and i['item_count'] < count:
            return await check_before_send(cb, "Не хватает товаров", shop_buy_inline)

        if i['item_id'] == item_id:
            new_count = i['item_count'] - count
            is_trader_count = new_count

            await db.update_trader_hero('item_count', new_count, item_id, hero.id)

    if is_trader_count is None:
        trader_count = item['item_count'] - count

        await db.add_trader_hero(hero.id, item_id, 1, trader_count)
        await db.update_heroes('money', hero.money, hero.id)

    inventory = await db.get_hero_inventory_all(hero.id)
    update = None

    for i in inventory:
        if i['item_id'] == item_id and i['is_stack'] is True:
            new_count = count + int(i['count'])
            update = await db.update_hero_inventory('count', new_count, hero.id, item_id)

    if update is None:
        await db.add_hero_inventory(hero.id, item_id, count, True, True)

    hero.money -= price

    items = await db.get_trader_items(1)
    kb = list_inline(items)

    await LocationState.store.set()
    return await cb.message.edit_text('Спасибо за покупку!', reply_markup=kb)


def shop(dp: Dispatcher):
    dp.register_callback_query_handler(buy_item, state=ShopState.buy)
