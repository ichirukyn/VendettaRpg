import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from tgbot.api.enemy import get_enemy_loot
from tgbot.api.statistic import statistics_to_json
from tgbot.api.statistic import update_statistic
from tgbot.handlers.battle.hook import BattleEngine
from tgbot.handlers.battle.hook import BattleLogger
from tgbot.keyboards.reply import arena_kb
from tgbot.keyboards.reply import battle_main_kb
from tgbot.keyboards.reply import battle_revival_kb
from tgbot.keyboards.reply import battle_sub_kb
from tgbot.keyboards.reply import confirm_kb
from tgbot.keyboards.reply import home_kb
from tgbot.keyboards.reply import list_kb
from tgbot.keyboards.reply import list_object_kb
from tgbot.keyboards.reply import next_kb
from tgbot.misc.hero import check_hero_lvl
from tgbot.misc.hero import init_hero
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import BattleState
from tgbot.misc.state import LocationState
from tgbot.models.api.enemy_api import EnemyItemType
from tgbot.models.entity.hero import Hero
from tgbot.models.user import DBCommands


class BattleInterface:
    def __init__(self, message, state, db, engine, logger):
        self.message: Message = message
        self.state: FSMContext = state
        self.db: DBCommands = db
        self.engine: BattleEngine = engine
        self.logger: BattleLogger = logger
        self.engine_data = None

        self.dp: Dispatcher = message.bot.get('dp')

    async def save_battle(self, state_name=None, state=None):
        for player in self.engine.order:
            if isinstance(player, Hero):
                if state_name is not None and state is not None:
                    await self.update_data(player.chat_id, state_name, state)

                await self.update_data(player.chat_id, 'engine_data', self.engine_data)
                await self.update_data(player.chat_id, 'engine', self.engine)
                await self.update_data(player.chat_id, 'logger', self.logger)

    async def check_index(self):
        data = await self.state.get_data()
        order_index = data.get('order_index')
        order = data.get('order')

        if order_index is None:
            order_index = self.engine.order_index

        if order is None:
            order = self.engine.order

        if order_index == len(order) - 1:
            await self.save_battle('order_index', 0)

    async def set_state(self, chat_id, state):
        await self.dp.storage.set_state(chat=chat_id, state=state)

    async def update_data(self, chat_id, state_name, state):
        data = dict()
        data[state_name] = state

        await self.dp.storage.update_data(chat=chat_id, **data)

    async def check_hp(self):
        team_win = self.engine.check_hp()

        if team_win is not None:
            self.handler_battle_end_start(team_win)
            return True

        return False

    async def start_battle(self):
        log = self.logger.battle_order(self.engine.order)
        await self.message.answer(log)
        await self.battle()

    async def battle(self):
        order, entity, who, i, log = self.engine.battle()
        move = entity.debuff_control_check('move')

        state = await self.state.get_state()

        if who == 'win' or state == BattleState.end.state:
            return await self.check_hp()

        if not move:
            if isinstance(entity, Hero):
                await self.set_state(entity.chat_id, BattleState.load)

            if log is not None:
                await self.send_all(entity, log, log, None, next_kb)

            order, entity, who, i, log = self.engine.battle()
        elif log is not None:
            await self.send_all(entity, log, log, None, next_kb)

        if who == 'hero':
            self.handler_user_turn_start(order, entity)
        else:
            self.handler_npc_turn_start(entity)

        # TODO: Переписать под вызов 1 функции с нескольми стейтами, или по другому реализовать
        await self.save_battle('order_index', i)
        await self.save_battle('order', order)

        await self.check_index()

    async def send_battle_logs(self, order, hero, kb, kb_h):
        for e in order:
            if e.name != hero.name:
                logs = self.logger.enemys_log(order, e) + f'Ход {hero.name}'
                kb_to_use = kb
            else:
                logs = self.logger.enemys_log(order, e) + 'Твой ход:'
                kb_to_use = kb_h

            if isinstance(e, Hero):
                await self.message.bot.send_message(chat_id=e.chat_id, text=logs, reply_markup=kb_to_use,
                                                    parse_mode='Markdown')

    async def send_all(self, hero, text, text_hero, kb, kb_h):
        for e in self.engine.order:
            if isinstance(e, Hero):
                if e.name != hero.name:
                    await self.message.bot.send_message(chat_id=e.chat_id, text=text, reply_markup=kb,
                                                        parse_mode='Markdown')
                else:
                    await self.message.bot.send_message(chat_id=e.chat_id, text=text_hero, reply_markup=kb_h,
                                                        parse_mode='Markdown')

    # HANDLERS

    def handler_npc_turn_start(self, hero):
        asyncio.create_task(self.handler_npc_turn(hero))

    async def handler_npc_turn(self, npc):
        await self.process_battle_action(npc, npc.target)

    def handler_user_turn_start(self, order, hero):
        asyncio.create_task(self.handle_user_turn(order, hero))

    async def handle_user_turn(self, order, hero):
        await self.update_data(hero.chat_id, 'hero', hero)

        await self.set_state(hero.chat_id, BattleState.user_turn)
        await self.send_battle_logs(order, hero, ReplyKeyboardRemove(), battle_main_kb)

    async def process_user_sub_turn(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == 'Уклонение':
            hero.sub_action = 'Уклонение'
            self.engine.save_entity(hero)

            await self.set_state(hero.chat_id, BattleState.load)

            text = f'{hero.name} пробует уклонится.'

            await self.send_all(hero, text, text, None, next_kb)
            return await self.battle()

        if message.text == 'Защита':
            hero.sub_action = 'Защита'
            self.engine.save_entity(hero)

            await self.set_state(hero.chat_id, BattleState.load)

            text = f'{hero.name} поставил блок.'

            await self.send_all(hero, text, text, None, next_kb)
            return await self.battle()

        if message.text == 'Контрудар':
            hero.sub_action = 'Контрудар'
            self.engine.save_entity(hero)

            await self.set_state(hero.chat_id, BattleState.load)

            text = f'{hero.name} ждёт момент для контрудара.'

            await self.send_all(hero, text, text, None, next_kb)
            return await self.battle()

        # TODO: Добавить подтверждение
        if message.text == 'Сбежать':
            await self.set_state(hero.chat_id, BattleState.user_escape_confirm)
            await message.answer('Вы уверены что хотите сбежать?', reply_markup=confirm_kb)

    async def process_user_escape_confirm(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == keyboard['yes']:
            hero.hp = 0
            hero.statistic.escape_count += 1

            await state.update_data(hero=hero)

            for e in self.engine.order:
                if e.name == hero.name:
                    e.hp = 0
                    e.sub_action = 'Сбежать'
                    hero.sub_action = 'Сбежать'

            text = f'{hero.name} сбегает..'

            await self.set_state(hero.chat_id, LocationState.home)
            await self.save_battle('order', self.engine.order)
            await self.send_all(hero, text, text, None, home_kb)

            await self.battle()
            return await self.check_hp()

        elif message.text == keyboard['back']:
            await self.set_state(hero.chat_id, BattleState.user_sub_turn)
            return await message.answer(f'Выбери доп. действие:', reply_markup=battle_sub_kb)

    async def process_user_pass_confirm(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == keyboard['yes']:
            text = f'{hero.name} пропустил ход.'

            await self.set_state(hero.chat_id, BattleState.user_sub_turn)
            return await self.send_all(hero, text, text, None, battle_sub_kb)

        elif message.text == keyboard['back']:
            await self.set_state(hero.chat_id, BattleState.user_turn)
            return await message.answer(f'Твой ход:', reply_markup=battle_main_kb)

    async def process_user_turn(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == keyboard['technique_list']:
            hero.action = keyboard['technique_list']
            await self.state.update_data(hero=hero)

            kb = list_kb(hero.techniques)

            await self.set_state(hero.chat_id, BattleState.select_technique)
            await message.answer('Выбери технику:', reply_markup=kb)

        elif message.text == keyboard['spell_list']:
            hero.action = keyboard['spell_list']
            await self.state.update_data(hero=hero)

            kb = list_object_kb(hero.skills)

            await self.set_state(hero.chat_id, BattleState.select_skill)
            await message.answer('Выбери заклинание:', reply_markup=kb)

        elif message.text == keyboard['pass']:
            await self.set_state(hero.chat_id, BattleState.user_pass_confirm)
            await message.answer('Вы уверены что хотите пропустить ход?', reply_markup=confirm_kb)

        await self.update_data(hero.chat_id, 'hero', hero)

    async def process_select_skill(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == keyboard["back"]:
            await self.set_state(hero.chat_id, BattleState.user_turn)
            return await message.answer(f'Твой ход:', reply_markup=battle_main_kb)

        for skill in hero.skills:
            if skill.name == message.text:
                hero.select_skill = skill
                await self.update_data(hero.chat_id, 'hero', hero)

                text = f"{skill.name}\n{skill.desc}\n\nВы уверены?"

                await self.set_state(hero.chat_id, BattleState.select_skill_confirm)
                return await message.answer(text, reply_markup=confirm_kb)

    async def process_select_skill_confirm(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        is_return = False
        text = ''
        kb = []

        if message.text == keyboard["back"]:
            text = 'Выбери заклинание:'
            is_return = True
            kb = list_object_kb(hero.skills)

        elif hero.is_active_skill(message.text):
            text = 'Заклинание уже активировано'
            is_return = True
            kb = list_object_kb(hero.skills)

        if is_return:
            await self.set_state(hero.chat_id, BattleState.select_skill)
            return await message.answer(text, reply_markup=kb)

        # TODO: Добавить выбор союзников
        await self.set_state(hero.chat_id, BattleState.user_sub_turn)
        await self.process_battle_action(hero, hero.target)

    async def process_select_technique(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == keyboard["back"]:
            await self.set_state(hero.chat_id, BattleState.user_turn)
            return await message.answer(f'Твой ход:', reply_markup=battle_main_kb)

        for technique in hero.techniques:
            if message.text.strip() == technique.name.strip():
                root_check = technique.distance != 'distant' or technique.type == 'support'

                if not hero.debuff_control_check('turn') and not root_check:
                    text = f'Вы под эффектом контроля и не можете применить {technique.name}'
                    await self.set_state(hero.chat_id, BattleState.user_turn)
                    return await message.answer(text, reply_markup=battle_main_kb)

                if technique.check(hero):
                    hero.technique = technique
                    await self.update_data(hero.chat_id, 'hero', hero)
                    await self.set_state(hero.chat_id, BattleState.select_technique_confirm)
                    return await message.answer(technique.technique_info(hero), reply_markup=confirm_kb)
                else:
                    text = technique.log or 'Ошибка активации..'
                    await self.set_state(hero.chat_id, BattleState.user_turn)
                    return await message.answer(text, reply_markup=battle_main_kb)

    async def process_select_technique_confirm(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == keyboard["back"]:
            kb = list_kb(hero.techniques)

            await self.set_state(hero.chat_id, BattleState.select_technique)
            return await message.answer('Выбери технику:', reply_markup=kb)

        return await self.handler_select_target(message, state)

    async def process_battle_action(self, hero, target):
        action_result = self.engine.battle_action(hero, target, hero.select_skill)

        if action_result is not None:
            if action_result['target'] is not None:
                self.engine.save_entity(action_result['target'])

            self.engine.save_entity(action_result['attacker'])

            if isinstance(hero, Hero):
                await self.update_data(hero.chat_id, 'hero', action_result['attacker'])
                await self.set_state(hero.chat_id, BattleState.user_sub_turn)

                await self.send_all(hero, action_result['log'], action_result['log'], None, battle_sub_kb)

                await self.save_battle()
                await self.check_hp()
            else:
                await self.send_all(hero, action_result['log'], action_result['log'], None, None)
                await self.save_battle()

                if await self.check_hp():
                    return

                await self.battle()

    async def handler_select_target(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        target_team = None
        text = ''
        target = hero.technique_target()

        if target == 'my' and hero.technique.damage == 0:
            return await self.process_battle_action(hero, hero)

        elif target == 'enemy':
            text = 'Выбери противника:'
            target_team = self.engine.target_enemy_team(hero)

            if len(target_team) == 1:
                return await self.process_battle_action(hero, target_team)

        elif target == 'teammate':
            text = 'Выбери союзника:'
            target_team = self.engine.target_teammate_team(hero)

        elif target == 'enemies':
            target_team = self.engine.target_enemy_team(hero)
            return await self.process_battle_action(hero, target_team)

        elif target == 'teammates':
            target_team = self.engine.target_teammate_team(hero)
            return await self.process_battle_action(hero, target_team)

        elif target == 'enemy' or hero.technique.damage != 0:
            text = 'Выбери противника:'
            target_team = self.engine.target_enemy_team(hero)

        if target_team is not None:
            kb = arena_kb(target_team)
            await self.update_data(hero.chat_id, 'target_team', target_team)

            await self.set_state(hero.chat_id, BattleState.select_target)
            await message.answer(text, reply_markup=kb)
            await self.save_battle()

    async def process_select_target(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')
        target_enemy_team = data.get('target_team')

        if message.text == keyboard["back"]:
            await self.set_state(hero.chat_id, BattleState.user_turn)
            return await message.answer(f'Твой ход:', reply_markup=battle_main_kb)

        for e in target_enemy_team:
            if message.text.strip(' ') == e.name.strip(' '):
                hero.target = e
                await self.process_battle_action(hero, hero.target)

    def handler_battle_end_start(self, team_win):
        asyncio.create_task(self.handler_battle_end(team_win))

    # TODO: Допилить систему опыта для боссов, функция всё равно сработает, когда противники победят, почему бы и нет?..
    async def handler_battle_end(self, team_win):
        session = self.message.bot.get('session')
        db = DBCommands(self.message.bot.get('db'))

        try:
            for e in self.engine.order:
                if isinstance(e, Hero) and e.sub_action != 'Сбежать':
                    log = 'Бой окончен'
                    await self.set_state(e.chat_id, BattleState.end)
                    await self.message.bot.send_message(chat_id=e.chat_id, text=log, reply_markup=ReplyKeyboardRemove())

            for e in self.engine.order:
                log = 'Вы проиграли..'
                kb = battle_revival_kb
                state = BattleState.revival
                is_inline = False

                if e in team_win and isinstance(e, Hero):
                    log = self.engine_data.get('exit_message', '')
                    kb = self.engine_data.get('exit_kb', home_kb)
                    state = self.engine_data.get('exit_state', LocationState.home)
                    is_inline = self.engine_data.get('is_inline', False)

                    log += '*Вы победили!*\n'
                    log += await self.battle_reward(e, session)

                    if self.engine.battle_type == 'arena_one':
                        e.statistic.win_one_to_one += 1

                    if self.engine.battle_type == 'arena_team':
                        e.statistic.win_team_to_team += 1
                elif isinstance(e, Hero):
                    if self.engine.battle_type == 'arena_one':
                        e.statistic.lose_one_to_one += 1

                    if self.engine.battle_type == 'arena_team':
                        e.statistic.lose_team_to_team += 1

                if isinstance(e, Hero):
                    e.statistic.battle_update(e.statistic.battle)
                    statistics = statistics_to_json(e.statistic)
                    await update_statistic(session, statistics, e.id)

                if isinstance(e, Hero):
                    if self.engine.is_dev:
                        log += f"\n\n{e.statistic.battle.get_battle_statistic()}"

                    if e.sub_action != 'Сбежать':
                        if is_inline:
                            await self.message.bot.send_message(
                                chat_id=e.chat_id, text='⁢', reply_markup=ReplyKeyboardRemove()
                            )

                        e = await init_hero(db, session, hero_id=e.id)
                        await self.set_state(e.chat_id, state)
                        await self.message.bot.send_message(chat_id=e.chat_id, text=log, reply_markup=kb)
                        await self.update_data(e.chat_id, 'hero', e)
        except Exception as e:
            print(e)

            for e in self.engine.order:
                if isinstance(e, Hero) and e.sub_action != 'Сбежать':
                    await self.set_state(e.chat_id, BattleState.end)
                    await self.message.bot.send_message(chat_id=e.chat_id, text=locale['error_battle'])

    # TODO: Навести порядок, вынести в отдельный модуль EXP
    async def battle_reward(self, e, session):
        enemies = self.engine.target_enemy_team(e, False)
        loot_list: [EnemyItemType] = []
        total_reward_exp = 0
        total_reward_gold = 0

        for enemy in enemies:
            loot = await get_enemy_loot(session, enemy.id, e.id)

            if loot is not None and len(loot) != 0:
                for l in loot:
                    loot_list.append(l)

        log = 'Вы получили:\n'

        for loot in loot_list:
            total_reward_exp += loot.get('exp', 0)
            total_reward_gold += loot.get('gold', 0)

            if loot.get('item_id', 0) != 0:
                log += f"{loot.get('item').get('name', 'Предмет')} {loot.get('count')}\n"

        log += f'Опыт {total_reward_exp}\n'
        log += f'Золото {total_reward_gold}\n'

        e.exp += int(total_reward_exp)
        e.exp_now += int(total_reward_exp)

        # TODO: Против "фармил", которые живут ареной и пока не сделаю норм опыт....
        if e.lvl > 20:
            return (
                f'Вы достигли предела... \n'
                f'Пополните баланс, чтобы продолжить)) \n'
            )

        lvl_log, e = await check_hero_lvl(self.db, session, e)
        log += lvl_log

        return log

    @staticmethod
    async def process_revival(message: Message, state: FSMContext):
        if message.text == 'Возрождение':
            await LocationState.home.set()

            data = await state.get_data()

            hero = data['hero']
            hero.default_stats()

            await state.update_data(hero=hero)

            await message.answer(locale['revival'])
            await message.answer(locale['greeting'], reply_markup=home_kb, parse_mode='Markdown')


class BattleFactory:
    def __init__(self, enemy_team, player_team, exit_state, exit_message, exit_kb, battle_type='battle', is_dev=False,
                 is_inline=False):
        self.enemy_team = enemy_team
        self.player_team = player_team

        self.exit_state = exit_state
        self.exit_message = exit_message
        self.exit_kb = exit_kb
        self.is_dev = is_dev
        self.battle_type = battle_type

    def create_battle_engine(self):
        return BattleEngine(self.enemy_team, self.player_team, self.exit_state, self.exit_message,
                            self.exit_kb, self.battle_type, is_dev=self.is_dev)

    def create_battle_logger(self):
        return BattleLogger(self.is_dev)

    @staticmethod
    def create_battle_interface(message, state, db, engine, logger):
        return BattleInterface(message, state, db, engine, logger)
