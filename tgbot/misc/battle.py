import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.keyboards.reply import battle_main_kb, arena_kb
from tgbot.keyboards.reply import battle_revival_kb, next_kb, battle_sub_kb, list_kb, home_kb, list_object_kb, \
    confirm_kb
from tgbot.misc.locale import locale
from tgbot.misc.other import formatted
from tgbot.misc.state import BattleState, LocationState
from tgbot.models.entity.hero import Hero
from tgbot.models.user import DBCommands


async def hero_victory(hero, money, message, state):
    data = await state.get_data()
    hero_id = data.get('hero_id')
    db = DBCommands(message.bot.get('db'))

    hero.money += int(money)
    hero.default_stats()

    # await hero_save_on_team(hero, state)
    await state.update_data(hero=hero)

    await db.update_heroes('money', hero.money, hero_id)

    await LocationState.arena.set()
    return await message.answer(f"Ты победил!\nТвоя награда:\n{formatted(money)} иен.", reply_markup=next_kb)


def escape(hero_speed, enemy_speed, success_threshold):
    if hero_speed >= enemy_speed:
        return True

    speed_ratio = enemy_speed / hero_speed

    return speed_ratio > success_threshold


class BattleEngine:
    def __init__(self, enemy_team, player_team, exit_state, exit_message, exit_kb):
        self.enemy_team = enemy_team
        self.player_team = player_team
        self.order = []
        self.order_index = 0

        # self.leader: Hero = hero

        self.exit_state = exit_state
        self.exit_message = exit_message
        self.exit_kb = exit_kb

        self.battle_result = None
        self.team_win = None
        self.logs = ''

    def initialize(self):
        self.order = self.update_order()

    def update_order(self):
        order = self.player_team + self.enemy_team
        order.sort(key=lambda x: x.speed, reverse=True)

        return order

    def battle(self):
        i = self.order_index

        while i < len(self.order):
            entity = self.order[i]
            entity.check_active_skill()

            log = self.check_durability(entity)
            self.order_index += 1

            if entity.hp <= 0:
                return self.battle()

            if isinstance(entity, Hero):
                who = 'hero'

            else:
                target_enemy_team = self.target_enemy_team(entity)

                if len(target_enemy_team) == 0:
                    return self.check_hp()

                entity.select_target(target_enemy_team)
                entity.define_action()
                entity.define_sub_action(target_enemy_team)
                entity.choice_technique()

                who = 'enemy'

            return self.order, entity, who, i, log

        self.order_index = 0
        return self.battle()

    # TODO: Расширить функцию, на проверку станов, и отрицательных эффектов
    def check_durability(self, entity):
        log = None

        if (entity.durability <= 0):
            log = f"🌀 Стойкость {entity.name} пробита, он пропускает ход."
            entity.durability = entity.durability_max

        return log

    def battle_action(self, attacker, defender, skill):
        action_return = {'name': attacker.action, 'target': defender, 'attacker': attacker}

        if attacker.action == 'Атака':
            action_return['log'] = self.entity_attack(attacker, defender)

            if action_return['target'].hp <= 0:
                log = f"\n💀 {action_return['target'].name} побежден."
                action_return['log'] += log

        elif attacker.action == 'Навыки':
            log = skill.skill_activate()
            action_return['log'] = log
            action_return['attacker'] = skill.hero

        return action_return

    def entity_attack(self, attacker, defender):
        log = ''
        hp = attacker.hp

        if attacker.durability <= 0:
            log = f"🌀 Стойкость {attacker.name} пробита, он пропускает ход."
            attacker.durability = attacker.durability_max
            return log

        if defender.hp > 0:
            # TODO: Заменить хардкод на класс техники
            total_damage = attacker.damage(defender, 'phys_damage')
            defender.hp -= total_damage

            if total_damage == 0:
                # TODO: Добавить условие для вывода клана, если есть
                log = f"⚔️ {attacker.name} промахнулся"
            else:
                defender.durability -= 20

                if attacker.technique_name != '':
                    log = f"⚔️ {attacker.name} использовал \"{attacker.technique_name}\" по {defender.name} и нанес {formatted(total_damage)} урона.\n"

                else:
                    log = f"⚔️ {attacker.name} атаковал {defender.name} и нанес {formatted(total_damage)} урона.\n"

            if hp > attacker.hp:
                delta = hp - attacker.hp
                log += f'🪃 {defender.name} контратаковал на {formatted(delta)} урона.'

        # if attacker.hp <= 0:
        #     log = f"{attacker.name} побежден."

        defender.sub_action = ''

        return log

    def save_entity(self, target):
        self.enemy_team = [enemy if enemy.name != target.name else target for enemy in self.enemy_team]
        self.player_team = [hero if hero.name != target.name else target for hero in self.player_team]

        self.order = self.update_order()

    def target_enemy_team(self, target):
        team = self.enemy_team

        for enemy in self.enemy_team:
            if target.name == enemy.name:
                team = self.player_team

        team = [e for e in team if e.hp > 0]

        return team

    def round_hp(self):
        for enemy in self.enemy_team:
            if enemy.hp < 0:
                enemy.hp = 0

        for player in self.player_team:
            if player.hp < 0:
                player.hp = 0

    # TODO: Условия победы в пвп добавить
    def check_hp(self):
        self.round_hp()

        enemy = max(self.enemy_team, key=lambda x: x.hp)
        player = max(self.player_team, key=lambda x: x.hp)

        if enemy.hp <= 0:
            print('Player win')
            return self.player_team
        elif player.hp <= 0:
            print('Enemy win')
            return self.enemy_team

        return None

    def check_pvp(self):
        for e in self.enemy_team:
            if e.chat_id is not None:
                return True

        return False


class BattleLogger:
    def __init__(self):
        self.loss = "Ты проиграл и в последствие был убит."

    def enemys_log(self, order, hero):
        logs = ''

        for entity in order:
            if entity.name != hero.name:
                logs += f"*{entity.name}: \n❤️ {formatted(entity.hp)}  🛡{formatted(entity.durability)}\n\n*"
            elif isinstance(entity, Hero):
                logs += f"*🌟 {hero.name}: \n❤️ {formatted(hero.hp)}  🛡{formatted(hero.durability)}\n*" \
                        f"*🔹{formatted(hero.mana_max)}/{formatted(hero.mana)}*\n" \
                        f"*{hero.info.active_bonuses()}*\n\n"

        return logs

    def battle_order(self, order):
        response = "Последовательность действий:\n"

        i = 1
        for e in order:
            response += f"{i}. {e.name}\n"
            i += 1

        return response


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

            await self.handler_battle_end(order, team_win)

    async def start_battle(self):
        log = self.logger.battle_order(self.engine.order)
        await self.message.answer(log)
        await self.battle()

    async def battle(self):
        order, entity, who, i, log = self.engine.battle()

        if log is not None:
            if isinstance(entity, Hero):
                await self.set_state(entity.chat_id, BattleState.load)

            await self.send_all(entity, log, log, None, next_kb)
            order, entity, who, i, log = self.engine.battle()

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
        await self.process_battle_action(npc, npc.target, npc.select_skill)

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

            await self.set_state(hero.chat_id, BattleState.user_turn)

            text = f'{hero.name} пробует уклонится.'

            await self.set_state(hero.chat_id, BattleState.load.set)
            await self.send_all(hero, text, text, None, next_kb)
            return await self.battle()

        if message.text == 'Защита':
            hero.sub_action = 'Защита'
            self.engine.save_entity(hero)

            await self.set_state(hero.chat_id, BattleState.user_turn)

            text = f'{hero.name} поставил блок.'

            await self.set_state(hero.chat_id, BattleState.load.set)
            await self.send_all(hero, text, text, None, next_kb)
            return await self.battle()

        if message.text == 'Контрудар':
            hero.sub_action = 'Контрудар'
            self.engine.save_entity(hero)

            await self.set_state(hero.chat_id, BattleState.user_turn)

            text = f'{hero.name} ждёт момент для контрудара.'

            await self.set_state(hero.chat_id, BattleState.load.set)
            await self.send_all(hero, text, text, None, next_kb)
            return await self.battle()

        # TODO: Добавить подтверждение
        if message.text == 'Сбежать':
            hero.hp = 0

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

        if message.text == 'Атака':
            hero.action = 'Атака'
            await self.state.update_data(hero=hero)

            techniques = await self.db.get_hero_techniques(hero.id)
            kb = list_kb(techniques)

            await self.set_state(hero.chat_id, BattleState.select_technique)
            await message.answer('Выбери технику:', reply_markup=kb)

        elif message.text == 'Навыки':
            hero.action = 'Навыки'
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

        if message.text == '🔙 Назад':
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

        if message.text == '🔙 Назад':
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
        await self.process_battle_action(hero, hero.target, message)

    async def process_select_technique(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        if message.text == '🔙 Назад':
            await self.set_state(hero.chat_id, BattleState.user_turn)
            return await message.answer(f'Твой ход:', reply_markup=battle_main_kb)

        techniques = await self.db.get_hero_techniques(hero.id)

        for technique in techniques:
            if message.text in technique['name']:
                hero.technique_name = technique['name']
                hero.technique_damage = technique['damage']
                await self.update_data(hero.chat_id, 'hero', hero)

                await self.handler_select_target(message, state)

    async def process_battle_action(self, hero, target, message):
        action_result = self.engine.battle_action(hero, target, hero.select_skill)

        if action_result is not None:
            if action_result['target'] is not None:
                self.engine.save_entity(action_result['target'])

            self.engine.save_entity(action_result['attacker'])

            if isinstance(hero, Hero):
                await self.update_data(hero.chat_id, 'hero', action_result['attacker'])
                await self.set_state(hero.chat_id, BattleState.user_sub_turn)

                await self.send_all(hero, action_result['log'], action_result['log'], None, battle_sub_kb)
            else:
                await self.send_all(hero, action_result['log'], action_result['log'], None, None)

                await self.check_hp()
                await self.save_battle()
                return await self.battle()

            await self.check_hp()
            await self.save_battle()

    async def handler_select_target(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')

        # Противники текущего существа, а не команда нпс
        target_enemy_team = self.engine.target_enemy_team(hero)

        text = 'Выбери противника:'
        kb = arena_kb(target_enemy_team)
        await self.update_data(hero.chat_id, 'target_enemy_team', target_enemy_team)

        await self.set_state(hero.chat_id, BattleState.select_target)
        await message.answer(text, reply_markup=kb)
        await self.save_battle()

    async def process_select_target(self, message: Message, state: FSMContext):
        data = await state.get_data()
        hero = data.get('hero')
        target_enemy_team = data.get('target_enemy_team')

        for e in target_enemy_team:
            if message.text.strip(' ') == e.name.strip(' '):
                hero.target = e
                await self.process_battle_action(hero, hero.target, message)

    def handler_battle_end_start(self, order, team_win):
        asyncio.create_task(self.handler_battle_end(order, team_win))

    async def handler_battle_end(self, order, team_win):
        for e in order:
            log = 'Вы проиграли..'
            kb = battle_revival_kb
            state = BattleState.revival

            for winner in team_win:
                if isinstance(e, Hero) and isinstance(winner, Hero):
                    if e.chat_id == winner.chat_id:
                        log = 'Вы победили!\n'
                        kb = self.engine.exit_kb
                        state = self.engine.exit_state

                        mod = len(order) - len(team_win) / 10
                        log += await self.battle_reward(e, mod)

                if isinstance(e, Hero) and e.sub_action != 'Сбежать':
                    await self.set_state(e.chat_id, state)
                    await self.message.bot.send_message(chat_id=e.chat_id, text=log, reply_markup=kb)

    async def battle_reward(self, e, mod):
        reward_exp = round(e.exp_reward(1 + mod))

        e.exp += int(reward_exp)
        log = f'Вы получили {reward_exp} опыта'

        # TODO: Против "фармил", которые живут ареной и пока не сделаю норм опыт....
        if e.lvl > 20:
            return f'Вы достигли предела, ждите обновление'

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

    async def process_revival(self, message: Message, state: FSMContext):
        if message.text == 'Возрождение':
            await LocationState.home.set()

            data = await state.get_data()

            hero = data['hero']
            hero.default_stats()

            await state.update_data(hero=hero)

            await message.answer(locale['revival'])
            await message.answer(locale['greeting'], reply_markup=home_kb, parse_mode='Markdown')


def unregister(dp: Dispatcher):
    dp.message_handlers.unregister('battle')
    dp.message_handlers.unregister('revival')
    dp.message_handlers.unregister('user_turn')
    dp.message_handlers.unregister('user_sub_turn')
    dp.message_handlers.unregister('select_technique')
    dp.message_handlers.unregister('select_target')
    dp.message_handlers.unregister('select_skill')
    dp.message_handlers.unregister('select_skill_confirm')


class BattleFactory:
    def __init__(self, enemy_team, player_team, exit_state, exit_message, exit_kb):
        self.enemy_team = enemy_team
        self.player_team = player_team

        self.exit_state = exit_state
        self.exit_message = exit_message
        self.exit_kb = exit_kb

    def create_battle_logger(self):
        return BattleLogger()

    def create_battle_engine(self):
        return BattleEngine(self.enemy_team, self.player_team, self.exit_state, self.exit_message,
                            self.exit_kb)

    def create_battle_interface(self, message, state, db, engine, logger):
        return BattleInterface(message, state, db, engine, logger)


# class BattleHandler:
def battle(dp):
    dp.register_message_handler(start_battle, state=BattleState.battle)
    dp.register_message_handler(revival, state=BattleState.revival)
    dp.register_message_handler(user_turn, state=BattleState.user_turn)
    dp.register_message_handler(user_sub_turn, state=BattleState.user_sub_turn)
    dp.register_message_handler(select_technique, state=BattleState.select_technique)
    dp.register_message_handler(select_target, state=BattleState.select_target)
    dp.register_message_handler(select_skill, state=BattleState.select_skill)
    dp.register_message_handler(select_skill_confirm, state=BattleState.select_skill_confirm)


async def start_battle(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    factory = BattleFactory(**engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    await ui.start_battle()


async def user_turn(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    factory = BattleFactory(**engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    await ui.process_user_turn(message, state)


async def user_sub_turn(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    factory = BattleFactory(**engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    await ui.process_user_sub_turn(message, state)


async def select_technique(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    factory = BattleFactory(**engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    await ui.process_select_technique(message, state)


async def select_skill(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    factory = BattleFactory(**engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    await ui.process_select_skill(message, state)


async def select_skill_confirm(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    factory = BattleFactory(**engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    await ui.process_select_skill_confirm(message, state)


async def select_target(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    factory = BattleFactory(**engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    await ui.process_select_target(message, state)


async def revival(message: Message, state: FSMContext):
    db = DBCommands(message.bot.get('db'))
    data = await state.get_data()
    engine_data = data['engine_data']
    engine = data['engine']
    logger = data['logger']

    factory = BattleFactory(**engine_data)
    ui = factory.create_battle_interface(message, state, db, engine, logger)
    ui.engine_data = engine_data

    await ui.process_revival(message, state)
