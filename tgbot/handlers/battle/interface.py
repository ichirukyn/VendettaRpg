import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

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
from tgbot.misc.locale import keyboard
from tgbot.misc.locale import locale
from tgbot.misc.state import BattleState
from tgbot.misc.state import LocationState
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
            data = await self.state.get_data()
            order = data.get('order')

            # await self.handler_battle_end(order, team_win)
            self.handler_battle_end_start(order, team_win)
            return True

        return False

    async def start_battle(self):
        log = self.logger.battle_order(self.engine.order)
        await self.message.answer(log)
        await self.battle()

    async def battle(self):
        order, entity, who, i, log = self.engine.battle()

        if log is not None and entity.debuff_control_check('move'):
            if isinstance(entity, Hero):
                await self.set_state(entity.chat_id, BattleState.load)

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

        if message.text == 'Уворот':
            hero.sub_action = 'Уворот'
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
            hero.hp = 0
            hero.statistic.escape_count += 1

            await state.update_data(hero=hero)

            for e in self.engine.order:
                if e.name == hero.name:
                    e.hp = 0
                    e.sub_action = 'Сбежать'

            text = f'{hero.name} сбегает..'

            await self.set_state(hero.chat_id, LocationState.home)
            await self.save_battle('order', self.engine.order)
            await self.send_all(hero, text, text, None, home_kb)

            await self.check_hp()

    async def process_user_turn(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == 'Техника':
            hero.action = 'Техника'
            await self.state.update_data(hero=hero)

            techniques = await self.db.get_hero_techniques(hero.id)
            kb = list_kb(techniques)

            await self.set_state(hero.chat_id, BattleState.select_technique)
            await message.answer('Выбери технику:', reply_markup=kb)

        elif message.text == 'Заклинания':
            hero.action = 'Заклинания'
            await self.state.update_data(hero=hero)

            kb = list_object_kb(hero.skills)

            await self.set_state(hero.chat_id, BattleState.select_skill)
            await message.answer('Выбери навык:', reply_markup=kb)

        elif message.text == 'Пас':
            text = f'{hero.name} пропустил ход.'

            await self.set_state(hero.chat_id, BattleState.user_sub_turn)
            return await self.send_all(hero, text, text, None, battle_sub_kb)

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
            text = 'Выбери навык:'
            is_return = True
            kb = list_object_kb(hero.skills)

        elif hero.is_active_skill(message.text):
            text = 'Навык уже активирован:'
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
            if message.text in technique.name:
                root_check = technique.distance != 'distant' or technique.type == 'support'

                if not hero.debuff_control_check('turn') and not root_check:
                    text = f'Вы под эффектом контроля и не можете применить {technique.name}'
                    await self.set_state(hero.chat_id, BattleState.user_turn)
                    return await message.answer(text, reply_markup=battle_main_kb)

                if technique.check():
                    hero.technique = technique
                    await self.update_data(hero.chat_id, 'hero', hero)

                    await self.handler_select_target(message, state)
                else:
                    text = f'Техника {technique.name} была активирована ранее (КД - {technique.cooldown} хода)'
                    await self.set_state(hero.chat_id, BattleState.user_turn)
                    return await message.answer(text, reply_markup=battle_main_kb)

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

        if target == 'my':
            return await self.process_battle_action(hero, hero)

        elif target == 'enemy':
            text = 'Выбери противника:'
            target_team = self.engine.target_enemy_team(hero)

        elif target == 'enemies':
            target_enemy_team = self.engine.target_enemy_team(hero)
            return await self.process_battle_action(hero, target_enemy_team)

        elif target == 'teammate':
            text = 'Выбери союзника:'
            target_team = self.engine.target_teammate_team(hero)

        elif target == 'teammates':
            target_teammate_team = self.engine.target_teammate_team(hero)
            return await self.process_battle_action(hero, target_teammate_team)

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

    def handler_battle_end_start(self, order, team_win):
        asyncio.create_task(self.handler_battle_end(order, team_win))

    async def handler_battle_end(self, order, team_win):
        for e in self.engine.order:
            log = 'Вы проиграли..'
            kb = battle_revival_kb
            state = BattleState.revival

            for winner in team_win:
                if isinstance(e, Hero) and isinstance(winner, Hero):
                    if e.chat_id == winner.chat_id:
                        log = 'Вы победили!\n'
                        kb = self.engine.exit_kb
                        state = self.engine.exit_state

                        teammate_count = len(order) - len(team_win)
                        print('teammate_count', teammate_count)
                        mod = teammate_count / 10

                        log += await self.battle_reward(e, mod, teammate_count)

                if isinstance(e, Hero) and self.engine.is_dev:
                    log += f"\n\n{e.statistic.battle.get_battle_statistic()}"
                    e.statistic.battle_update(e.statistic.battle)
                    statistics = statistics_to_json(e.statistic)
                    update_statistic(statistics, e.id)

                if isinstance(e, Hero) and e.sub_action != 'Сбежать':
                    await self.set_state(e.chat_id, state)
                    await self.message.bot.send_message(chat_id=e.chat_id, text=log, reply_markup=kb)

    # TODO: Навести порядок, вынести в отдельный модуль EXP
    async def battle_reward(self, e, mod, teammate_count):
        enemies = self.engine.target_enemy_team(e, False)

        total_reward = 0

        for enemy in enemies:
            total_reward += e.exp_reward(1 + mod, enemy.lvl)

        reward_exp = round(total_reward / teammate_count)

        e.exp += int(reward_exp)
        log = f'Вы получили {reward_exp} опыта'

        # TODO: Против "фармил", которые живут ареной и пока не сделаю норм опыт....
        if e.lvl > 20:
            return (
                f'Вы достигли предела... \n'
                f'Пополните баланс, чтобы продолжить)) \n'
            )

        if e.check_lvl_up():
            new_lvl = await self.db.get_hero_lvl_by_exp(e.exp)

            while e.lvl < new_lvl['max']:
                e.lvl += 1
                e.free_stats += 10  # TODO: Тянуть с ранга
                log += f"\n\nВы достигли {e.lvl} уровня!\nВы получили {10} СО"
                await self.db.update_hero_stat('free_stats', e.free_stats, e.id)

        await self.db.update_hero_level(e.exp, e.lvl, e.id)
        await self.update_data(e.chat_id, 'hero', e)

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
    def __init__(self, enemy_team, player_team, exit_state, exit_message, exit_kb, is_dev=False):
        self.enemy_team = enemy_team
        self.player_team = player_team

        self.exit_state = exit_state
        self.exit_message = exit_message
        self.exit_kb = exit_kb
        self.is_dev = is_dev

    def create_battle_engine(self):
        return BattleEngine(self.enemy_team, self.player_team, self.exit_state, self.exit_message,
                            self.exit_kb, self.is_dev)

    def create_battle_logger(self):
        return BattleLogger(self.is_dev)

    @staticmethod
    def create_battle_interface(message, state, db, engine, logger):
        return BattleInterface(message, state, db, engine, logger)
