from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tgbot.keyboards.inline import team_main_inline, list_inline, yes_no_inline, teammate_menu_inline
from tgbot.keyboards.reply import team_private_kb
from tgbot.misc.locale import locale
from tgbot.misc.state import TeamState, LocationState
from tgbot.models.user import DBCommands


async def team_add(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))

    if message.text == 'Нет':
        await to_team_main(message, state)
    else:
        data = await state.get_data()
        hero = data.get('hero')
        team_name = data.get('team_name')
        team_private = data.get('team_private')

        # TODO: Переписать на возвращение id с создания команды

        test = await db.add_team(hero.id, team_name, team_private)

        team_db = await db.get_hero_team(hero.id)

        await db.add_hero_team(hero.id, test['id'])

        await state.update_data(team_name='')
        await state.update_data(team_private=False)

        await message.answer('Вы создали группу!')
        await to_team_main(message, state)


async def team_add_name(message: Message, state: FSMContext):
    if message.text == '🔙 Назад':
        await to_team_main(message, state)

    name = message.text
    await state.update_data(team_name=name)

    await TeamState.add_private.set()
    await message.answer('Сделать команду приватной?\n(Она будет скрыта в общем списке)', reply_markup=team_private_kb)


async def team_add_private(message: Message, state: FSMContext):
    is_private = False

    if message.text == 'Нет':
        is_private = True

    await state.update_data(team_private=is_private)

    data = await state.get_data()
    team_name = data.get('team_name')

    text = f'Вы уверены что хотите создать группу {team_name}?'

    await TeamState.add.set()
    await message.answer(text, reply_markup=team_private_kb)


async def team_list(cb: CallbackQuery, state: FSMContext):
    db = DBCommands(cb.message.bot.get('db'))

    if cb.data == '🔙 Назад':
        return await to_team_main(cb.message, state)

    data = await state.get_data()
    hero = data.get('hero')

    if cb.data == 'Да':
        team_select = data.get('team_select')
        team = await db.get_team(team_select)
        leader = await db.get_user(team['leader_id'])

        await state.storage.update_data(chat=leader['chat_id'], send_invite_to_team=hero.id)
        await cb.message.bot.send_message(chat_id=leader['chat_id'], text=f"{hero.name} хочет присоединится к команде.")

        await LocationState.team.set()
        return await cb.message.edit_text('Вы отправили заявку!', reply_markup=team_main_inline())

    elif cb.data == 'Нет':
        teams = await db.get_teams()
        kb = list_inline(teams, cb_data='team_id')

        await TeamState.team_list.set()
        return await cb.message.edit_text('Список команд.\n (Нажмите, чтобы отправить заявку)', reply_markup=kb)

    team_id = int(cb.data)
    team = await db.get_team(team_id)
    await state.update_data(team_select=team_id)

    await cb.message.edit_text(f"Вы хотите вступить в {team['name']}?", reply_markup=yes_no_inline)


async def team_accept_leader(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()

    sender_id = data.get('send_invite_to_team')
    sender = await db.get_heroes(sender_id)

    hero = data.get('hero')

    if message.text == 'Отклонить':
        state.__delattr__('send_invite_to_team')
        await message.bot.send_message(chat_id=sender['chat_id'], text=f'{hero.name} отклонил вашу заявку')
        return await to_team_main(message, state)

    sender_team = await db.get_hero_team(sender_id)

    if sender_team is not None:
        state.__delattr__('send_invite_to_team')
        await message.answer('Игрок уже вступил в группу')
        return await to_team_main(message, state)

    team = await db.get_hero_team(hero.id)
    await db.add_hero_team(sender_id, team['team_id'])

    await message.bot.send_message(chat_id=sender['chat_id'], text='Вас приняли в команду!')
    await to_team_main(message, state)

    await message.answer('Вы приняли игрока в команду.')
    await to_team_main(message, state)


async def team_send_invite(message: Message, state: FSMContext):
    if message.text == '🔙 Назад':
        await to_team_main(message, state)

    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()

    hero = data.get('hero')

    try:
        id = int(message.text)
        leader_team_db = await db.get_hero_team(hero.id)
        hero_team_db = await db.get_hero_team(id)
        hero_db = await db.get_heroes(id)
        user_db = await db.get_user(hero_db['user_id'])

        if hero_db is None:
            return await message.answer('Такого игрока не существует.')

        if hero_team_db is not None:
            return await message.answer('Игрок уже состоит в команде.')

        await state.storage.update_data(chat=user_db['chat_id'], invite_team_id=leader_team_db['team_id'])
        await message.bot.send_message(chat_id=hero_db['chat_id'], text=f'{hero.name} Приглашает вас в команду.')
        await message.answer(f"Вы отправили приглашение {hero_db['name']}")
        return await to_team_main(message, state)

    except TypeError:
        await message.answer('Введите корректное число...')


async def team_accept_invite(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()

    if message.text == 'Отклонить':
        state.__delattr__('invite_team_id')
        await to_team_main(message, state)

    try:
        invite_team_id = data.get('invite_team_id')
        hero = data.get('hero')

        await db.add_hero_team(hero.id, invite_team_id)
        await message.answer('Вы вступили в команду!')
        await to_team_main(message, state)

    except KeyError:
        await message.answer('Произошла ошибка.. Попробуйте снова..')


async def teammate_list(cb: CallbackQuery, state: FSMContext):
    if cb.data == '🔙 Назад':
        await cb.message.delete()
        return await to_team_main(cb.message, state)

    data = await state.get_data()
    hero = data.get('hero')

    if hero.is_leader and int(cb.data) != hero.id:
        await state.update_data(teammate_id=int(cb.data))
        await TeamState.teammate_menu.set()
        await cb.message.edit_text('Выберите действие:', reply_markup=teammate_menu_inline)


async def teammate_menu(cb: CallbackQuery, state: FSMContext):
    if cb.data == '🔙 Назад':
        await cb.message.delete()
        return await to_team_main(cb.message, state)

    if cb.data == 'Исключить':
        await TeamState.kik.set()
        return await cb.message.edit_text('Вы уверены что хотите исключить игрока?', reply_markup=yes_no_inline)


async def team_kik(cb: CallbackQuery, state: FSMContext):
    if cb.data == 'Нет':
        await cb.message.delete()
        return await to_team_main(cb.message, state)

    db = DBCommands(cb.message.bot.get('db'))

    data = await state.get_data()
    hero = data.get('hero')
    teammate_id = data.get('teammate_id')

    teammate = await db.get_heroes(teammate_id)
    await db.del_hero_team(teammate_id)

    await cb.message.bot.send_message(chat_id=teammate['chat_id'], text='Вас исключили из группы...')

    is_team = False

    if hero.team_id != 0:
        is_team = True

    kb = team_main_inline(is_team, hero.is_leader)

    await LocationState.team.set()
    await cb.message.edit_text('Вы исключили игрока из группы.', reply_markup=kb)


async def to_team_main(message: Message, state: FSMContext):
    data = await state.get_data()
    hero = data.get('hero')

    is_team = False

    if hero.team_id != 0:
        is_team = True

    kb = team_main_inline(is_team, hero.is_leader)

    await LocationState.team.set()
    await message.answer('⁢', reply_markup=ReplyKeyboardRemove())
    await message.answer(locale['team'], reply_markup=kb)


def team(dp: Dispatcher):
    dp.register_message_handler(team_add, state=TeamState.add)
    dp.register_message_handler(team_add_name, state=TeamState.add_name)
    dp.register_message_handler(team_add_private, state=TeamState.add_private)

    dp.register_message_handler(team_send_invite, state=TeamState.send_invite)
    dp.register_message_handler(team_accept_invite, state=TeamState.accept_invite)
    dp.register_message_handler(team_accept_leader, state=TeamState.accept_leader)
    dp.register_callback_query_handler(team_list, state=TeamState.team_list)
    dp.register_callback_query_handler(teammate_list, state=TeamState.teammate_list)
    dp.register_callback_query_handler(teammate_menu, state=TeamState.teammate_menu)
    dp.register_callback_query_handler(team_kik, state=TeamState.kik)
    # dp.register_callback_query_handler(team_, state=TeamState.)
