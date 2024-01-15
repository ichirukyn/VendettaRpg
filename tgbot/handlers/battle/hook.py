from tgbot.misc.locale import keyboard
from tgbot.misc.other import formatted
from tgbot.models.entity._class import Class
from tgbot.models.entity.enemy import Enemy
from tgbot.models.entity.entity import Entity
from tgbot.models.entity.hero import Hero
from tgbot.models.entity.hero import HeroInfo
from tgbot.models.entity.race import Race
from tgbot.models.entity.statistic import Statistic
from tgbot.models.entity.statistic import StatisticBattle


class BattleEngine:
    def __init__(self, enemy_team, player_team, exit_state, exit_message, exit_kb, is_dev=False):
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
        self.is_dev = is_dev

    def initialize(self):
        self.order = self.update_order()

        # Очистка статистики предыдущей битвы
        for entity in self.order:
            if entity.statistic is not None:
                entity.statistic.battle = StatisticBattle()
            else:
                entity.statistic = Statistic()

    def update_order(self):
        order = self.player_team + self.enemy_team

        # TODO: Убрать, когда разберусь в чём баг
        try:
            order.sort(key=lambda x: x.speed, reverse=True)
        except:
            print("AttributeError: 'NoneType' object has no attribute 'speed'")

        return order

    def battle(self):
        i = self.order_index
        log = None

        while i < len(self.order):
            entity = self.order[i]

            entity.check_active_skill()
            entity.technique_cooldown()
            log = entity.debuff_round_check()

            self.order_index += 1

            if self.check_hp() is not None:
                return self.order, entity, 'win', i, log

            if entity.hp <= 0:
                return self.battle()

            if isinstance(entity, Hero):
                who = 'hero'

            else:
                enemies = self.target_enemy_team(entity)
                teammates = self.target_teammate_team(entity)

                entity.define_action()
                entity.sub_action = entity.define_sub_action(enemies)
                entity.choice_technique()
                entity.select_target(teammates, enemies)

                who = 'enemy'

            return self.order, entity, who, i, log

        self.order_index = 0
        return self.battle()

    def battle_action(self, attacker: Entity, defender, skill):
        action_return = {'name': attacker.action, 'target': defender, 'attacker': attacker, 'log': '⁢'}

        if attacker.action == keyboard['technique_list']:
            if not isinstance(defender, Hero) or not isinstance(defender, Enemy):
                action_return['log'] = self.entity_attack(attacker, defender)
            else:
                action_return['log'] = ''
                for target in defender:
                    action_return['log'] += self.entity_attack(attacker, target) + '\n'

            if action_return['target'].hp <= 0:
                log = f"\n💀 {action_return['target'].name} побежден."
                action_return['log'] += log

                # stats get
                defender.statistic.battle.death += 1

                if isinstance(defender, Hero):
                    attacker.statistic.battle.kill_hero += 1
                else:
                    attacker.statistic.battle.kill_enemy += 1

        elif attacker.action == keyboard['spell_list']:
            log = skill.activate()
            action_return['log'] = log
            action_return['attacker'] = skill.hero

        logger = BattleLogger(self.is_dev)
        action_return['log'] = logger.turn_log(attacker, defender, action_return['log'])

        return action_return

    def save_entity(self, target):
        self.enemy_team = [enemy if enemy.name != target.name else target for enemy in self.enemy_team]
        self.player_team = [hero if hero.name != target.name else target for hero in self.player_team]

        self.order = self.update_order()

    # Противники текущего существа, а не команда нпс
    def target_enemy_team(self, target, check_hp=True):
        team = self.enemy_team

        for enemy in self.enemy_team:
            if target.name == enemy.name:
                team = self.player_team

        if check_hp:
            team = [e for e in team if e.hp > 0]

        return team

    # TODO: Протестировать, правильно ли работает
    def target_teammate_team(self, target, check_hp=True):
        team = self.player_team

        for enemy in self.enemy_team:
            if target.name == enemy.name:
                team = self.enemy_team

        if check_hp:
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

    def get_hero(self, hero):
        for h in self.player_team:
            if h.id == hero.id:
                return h

    @staticmethod
    def entity_attack(attacker, defender):
        log = ''
        hp = attacker.hp
        hp_def = defender.hp

        log += attacker.technique.activate(defender)

        if attacker.name == defender.name:
            for attr in vars(defender):
                setattr(attacker, attr, getattr(defender, attr))

        if attacker.name == defender.name:
            log = f"{attacker.name} применил технику {attacker.technique.name}\n"
        else:
            log = f"{attacker.name} применил технику {attacker.technique.name} к {defender.name}\n"

        if attacker.technique.type == 'support' and attacker.technique.damage == 0:
            if attacker.hp > attacker.hp_max:
                attacker.hp = attacker.hp_max

            if defender.hp > defender.hp_max:
                defender.hp = defender.hp_max

            delta = 0
            if hp < attacker.hp:
                delta = attacker.hp - hp

            if hp_def < defender.hp:
                delta = defender.hp - hp

            if delta != 0:
                attacker.statistic.battle.healing += delta
                attacker.statistic.battle.check_max('healing_max', delta)
                log = f"{defender.name} восстановил ❤️{formatted(delta)}"

            attacker.update_stats_percent()
            defender.update_stats_percent()
            defender.sub_action = ''

            return log

        if defender.hp > 0:
            total_damage = attacker.damage(defender, attacker.technique.type_damage)
            defender.hp -= total_damage

            attacker.statistic.battle.damage += total_damage
            attacker.statistic.battle.check_max('damage_max', total_damage)
            defender.statistic.battle.damage_taken += total_damage
            defender.statistic.battle.check_max('damage_taken_max', total_damage)

            if total_damage == 0:
                # TODO: Добавить условие для вывода клана, если есть
                log = f"⚔️ {attacker.name} промахнулся"

                attacker.statistic.battle.miss_count += 1
                defender.statistic.battle.evasion_success_count += 1

            else:
                attacker.statistic.battle.hits_count += 1

                if attacker.technique.name != '':
                    log = f"⚔️ {attacker.name} использовал \"{attacker.technique.name}\" по {defender.name} " \
                          f"и нанес {formatted(total_damage)} урона.\n"

                else:
                    log = f"⚔️ {attacker.name} атаковал {defender.name} и нанес {formatted(total_damage)} урона.\n"

            if hp > attacker.hp:
                delta = hp - attacker.hp
                log += f'🪃 {defender.name} контратаковал на {formatted(delta)} урона.'

                attacker.statistic.battle.damage_taken += delta
                defender.statistic.battle.counter_strike_damage += delta
                defender.statistic.battle.counter_strike_count += 1

        attacker.update_stats_percent()
        defender.update_stats_percent()
        defender.sub_action = ''

        return log

    @staticmethod
    def escape(hero_speed, enemy_speed, success_threshold):
        if hero_speed >= enemy_speed:
            return True

        speed_ratio = enemy_speed / hero_speed

        return speed_ratio > success_threshold


class BattleLogger:
    def __init__(self, is_dev):
        self.loss = "Ты проиграл и в последствие был убит."
        self.is_dev = is_dev

    @staticmethod
    def enemys_log(order, hero):
        logs = ''

        for entity in order:
            if entity.name != hero.name:
                logs += f"*{entity.name}: \n❤️ {formatted(entity.hp)}\n\n*"
            elif isinstance(entity, Hero):
                logs += f"*🌟 {hero.name}: \n❤️ {formatted(hero.hp)}\n*" \
                        f"*🔹{formatted(hero.mana_max)}/{formatted(hero.mana)}*\n" \
                        f"*{hero.info.active_bonuses()}*\n" \
                        f"*{hero.info.active_debuff()}*\n"

        return logs

    @staticmethod
    def battle_order(order):
        response = "Последовательность действий:\n"

        i = 1
        for e in order:
            response += f"{i}. {e.name}\n"
            i += 1

        return response

    def turn_log(self, attacker, defender, log):
        if not self.is_dev:
            return log

        bonuses_a = self.get_effects(attacker)
        bonuses_d = self.get_effects(defender)

        debuffs_a = self.get_debuff(attacker)
        debuffs_d = self.get_debuff(defender)

        log = ''.join([
            log,
            f"\n\n",
            f"Атакующий: {attacker.name}\n",
            f"Тип: {attacker.action}\n",
            f"Цель: {defender.name}\n",
            f"\n",
            bonuses_a,
            debuffs_a,
            f"\n\n",
            defender.name,
            f"\n",
            bonuses_d,
            debuffs_d,
        ])

        return log

    @staticmethod
    def get_effects(entity):
        info = HeroInfo(entity)

        name_list = []
        bonuses = ''
        ignore_list = [Race, Class]  # Skill, Technique, etc..

        for bonus_wrap in entity.active_bonuses:
            if any(isinstance(bonus_wrap, ignored_class) for ignored_class in ignore_list):
                continue

            if bonus_wrap.name not in name_list:
                name_list.append(bonus_wrap.name)
                text = info.bonus_info(f'{entity.name} -- {bonus_wrap.name}\n', bonus_wrap.effects, True, True, True)

                if text is not None:
                    bonuses += text
        return bonuses

    @staticmethod
    def get_debuff(entity):
        debuffs = ''

        for debuff in entity.debuff_list:
            if debuff['type'] == 'control':
                debuffs += f"{debuff['name']} ({debuff.get('duration')})\n"
            if debuff['type'] == 'period':
                debuffs += f"{debuff.get('name', 'Периодический')}: " \
                           f"{entity.prev_period}/{entity.total_period} ({debuff.get('duration')})\n"

        return debuffs
