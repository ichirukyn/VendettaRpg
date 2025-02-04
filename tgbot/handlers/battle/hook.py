from tgbot.enums.skill import SkillSubAction
from tgbot.enums.skill import SkillType
from tgbot.misc.locale import keyboard
from tgbot.misc.other import formatted
from tgbot.models.entity._class import Class
from tgbot.models.entity.entity import Entity
from tgbot.models.entity.hero import Hero
from tgbot.models.entity.hero import HeroInfo
from tgbot.models.entity.race import Race
from tgbot.models.entity.statistic import Statistic
from tgbot.models.entity.statistic import StatisticBattle


class BattleEngine:
    def __init__(self, enemy_team, player_team, exit_state, exit_message, exit_kb, battle_type, is_dev=False,
                 callback=None):
        self.enemy_team = enemy_team
        self.player_team = player_team
        self.order = []
        self.order_index = 0

        # self.leader: Hero = hero

        self.exit_state = exit_state
        self.exit_message = exit_message
        self.exit_kb = exit_kb
        self.battle_type = battle_type

        self.battle_result = None
        self.team_win = None
        self.logs = ''
        self.is_dev = is_dev
        self.callback = callback
        self.round = 0

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

        while i < len(self.order):
            entity = self.order[i]

            if self.callback:
                for e in self.order:
                    e.turn += 1

                self.callback([self.player_team, self.enemy_team])

            if entity.sub_action is None or entity.sub_action == '':
                entity.sub_action = SkillSubAction.defense

            entity.check_active_effects()
            entity.skill_cooldown()
            entity.turn_regenerate()
            entity.decay_aggression()

            log = entity.debuff_round_check()

            self.order_index += 1

            if entity.hp <= 0:
                return self.battle()

            if isinstance(entity, Hero):
                who = 'hero'

            else:
                enemies = self.target_enemy_team(entity)
                teammates = self.target_teammate_team(entity)

                if len(enemies) < 1:
                    return self.order, None, 'win', i, ''

                entity.define_action()
                entity.sub_action = entity.define_sub_action(enemies)

                if entity.choice_technique():
                    entity.select_target(teammates, enemies)

                if entity.target is None:
                    entity.target = enemies[0]

                who = 'enemy'

            return self.order, entity, who, i, log

        if self.check_hp() is not None:
            return self.order, None, 'win', i, ''

        self.order_index = 0
        self.round += 1
        return self.battle()

    def battle_action(self, attacker: Entity, defender):
        if not isinstance(defender, list):
            defender = [defender]

        action_return = {
            'name': attacker.action,
            'target': [*defender],
            'attacker': attacker,
            'log': '⁢'
        }

        if attacker.action == keyboard['technique_list'] or attacker.action == keyboard['spell_list']:
            action_return['log'] = ''

            for target in action_return['target']:
                action_return['log'] += f"{self.entity_attack(attacker, target)}\n"

            for target in action_return['target']:
                if target.hp <= 0:
                    log = f"\n💀 {target.name} побежден."
                    action_return['log'] += log

                    # stats get
                    target.statistic.battle.death += 1

                    if isinstance(target, Hero):
                        attacker.statistic.battle.kill_hero += 1
                    else:
                        attacker.statistic.battle.kill_enemy += 1

        elif attacker.action == keyboard['pass']:
            action_return['log'] = f'{attacker.name} пропустил ход.'

        logger = BattleLogger(self.is_dev)
        action_return['log'] = logger.turn_log(attacker, action_return['target'], action_return['log'])

        return action_return

    def save_entity(self, target, attacker=None):
        if isinstance(target, list):
            for t in target:
                # TODO: Понять, почему вдруг None!!
                if t is None:
                    print('isinstance(target, list) -- error!!! \n\n')
                    continue

                if attacker is not None and t.name == attacker.name:
                    self.order = self.update_order()
                    return

                self.enemy_team = [enemy if enemy.name != t.name else t for enemy in self.enemy_team]
                self.player_team = [hero if hero.name != t.name else t for hero in self.player_team]

        else:
            if attacker is not None and target.name == attacker.name:
                self.order = self.update_order()
                return

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

    def escape_hero(self, hero):
        for e in self.order:
            if e.name == hero.name:
                e.hp = 0
                e.sub_action = SkillSubAction.escape
                hero.sub_action = SkillSubAction.escape

    # TODO: Условия победы в пвп добавить
    def check_hp(self):
        self.round_hp()

        enemy = max(self.enemy_team, key=lambda x: x.hp)
        player = max(self.player_team, key=lambda x: x.hp)

        if enemy.hp <= 0:
            return self.player_team
        elif player.hp <= 0:
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

    def entity_aggression(self, attacker, type, value=1):
        match type:
            case 'damage':
                attacker.update_aggression(damage=value)
            case 'heal':
                attacker.update_aggression(healing=value)
            case 'cc', 'skill':
                dps = HeroInfo().dps(attacker)
                attacker.update_aggression(cc=dps)

    def entity_attack(self, attacker, defender):
        hp = attacker.hp
        hp_def = defender.hp or 0

        action = attacker.technique

        if defender.sub_action is None or defender.sub_action == '':
            defender.sub_action = SkillSubAction.defense

        if attacker.spell is not None:
            action = attacker.spell

        if attacker.name != defender.name and defender.check_evasion(attacker):
            log = f"⚔️ {attacker.name} промахнулся по {defender.name}\n"
            attacker.aggression_combo = 1

            attacker.statistic.battle.miss_count += 1
            defender.statistic.battle.evasion_success_count += 1

            if action.type == SkillType.support:
                log += action.activate(attacker, defender)

            action.coast(attacker)
            return log

        if attacker.name == defender.name:
            action.activate(attacker, attacker)
            log = f"{attacker.name} применил технику {action.name}\n"
            self.entity_aggression(attacker, 'skill')
            defender = attacker
        else:
            action.activate(attacker, defender)
            log = f"{attacker.name} применил технику {action.name} к {defender.name}\n"
            self.entity_aggression(attacker, 'skill')

        if action.type == SkillType.support:
            attacker.check_shield()
            defender.check_shield()

            if attacker.hp > attacker.hp_max:
                attacker.hp = attacker.hp_max

            if defender.hp > defender.hp_max:
                defender.hp = defender.hp_max

            delta = 0
            if hp < attacker.hp:
                delta = attacker.hp - hp

            if hp_def < defender.hp:
                delta = defender.hp - hp

            # TODO: Сделать аналог для щитов..
            if delta != 0:
                attacker.statistic.battle.healing += delta
                attacker.statistic.battle.check_max('healing_max', delta)
                log = f"{defender.name} восстановил 🔻{formatted(delta)}"
                self.entity_aggression(attacker, 'heal', delta)

            attacker.update_stats_percent()
            defender.update_stats_percent()

            return log

        if defender.hp > 0:
            total_damage, damage_log = attacker.damage(defender, action.type_damage)

            if defender.shield > 0:
                delta = defender.shield - total_damage

                if delta <= 0:
                    defender.shield = 0
                    defender.hp -= delta * -1  # - на -, даёт +. Поэтому переворачиваем
                else:
                    defender.shield -= total_damage
            else:
                defender.hp -= total_damage

            if defender.shield <= 0:
                defender.shield_max = 0

            if attacker.shield <= 0:
                attacker.shield_max = 0

            attacker.statistic.battle.damage += total_damage
            attacker.statistic.battle.check_max('damage_max', total_damage)
            defender.statistic.battle.damage_taken += total_damage
            defender.statistic.battle.check_max('damage_taken_max', total_damage)

            attacker.statistic.battle.hits_count += 1

            self.entity_aggression(attacker, 'damage', total_damage)

            if total_damage == 0:
                log = f"⚔️ {attacker.name} использовал \"{action.name}\" на {defender.name}"

            else:
                log = f"⚔️ {attacker.name} использовал \"{action.name}\" на {defender.name} " \
                      f"и нанес {formatted(total_damage)} урона."

            if hp > attacker.hp:
                delta = hp - attacker.hp

                self.entity_aggression(defender, 'damage', delta)
                attacker.statistic.battle.damage_taken += delta
                defender.statistic.battle.counter_strike_damage += delta
                defender.statistic.battle.counter_strike_count += 1

            if damage_log is not None:
                log += damage_log

        attacker.update_stats_percent()
        defender.update_stats_percent()

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
        info = HeroInfo()

        for entity in order:
            if entity.name != hero.name:
                shield_log = f'`{formatted(entity.shield)}/{formatted(entity.shield_max)}`\n'

                logs += (
                    f"*{entity.name}:* \n`🔻 {formatted(entity.hp)}/{formatted(entity.hp_max)}\n`"
                    f"{shield_log if hero.shield_max > 0 else ''}"
                    f"{info.active_bonuses(entity) or ''}"
                    # f"{info.active_debuff(entity) or ''}"
                )
            elif isinstance(entity, Hero):
                shield_log = f'`🛡 {formatted(hero.shield)}/{formatted(hero.shield_max)}`\n'

                logs += (
                    f"*— {hero.name}:* \n`🔻 {formatted(hero.hp)}/{formatted(hero.hp_max)}\n`"
                    f"{shield_log if hero.shield_max > 0 else ''}"
                    f"`🔹{formatted(hero.mana)}/{formatted(hero.mana_max)} ({formatted(hero.mana_reg)})`\n"
                    f"`🔸{formatted(hero.qi)}/{formatted(hero.qi_max)} ({formatted(hero.qi_reg)})`\n"
                    f"{hero.info.active_bonuses(hero) or ''}"
                    # f"{hero.info.active_debuff(hero) or ''}"
                )
            logs += f"`———————————————————`\n"

        return logs

    @staticmethod
    def battle_order(order):
        response = "Последовательность действий:\n"

        i = 1
        for e in order:
            response += f"{i}. {e.name}\n"
            i += 1

        return response

    @staticmethod
    def get_hp(entity):
        if entity is None:
            return ''

        hp = ''

        if not isinstance(entity, list):
            entity = [entity]

        # Придумать как убрать отображение ошибки..
        for e in entity:
            hp = ''.join([hp, f"({e.hp}/{e.hp_max}) "])

        return hp

    def turn_log(self, attacker, defender, log):
        if not self.is_dev:
            return log

        bonuses_a = self.get_effects(attacker)
        debuffs_a = self.get_debuff(attacker)

        if isinstance(defender, list):
            bonuses_d = self.get_effects(defender[0])
            debuffs_d = self.get_debuff(defender[0])
            def_name = defender[0].name
        else:
            bonuses_d = self.get_effects(defender)
            debuffs_d = self.get_debuff(defender)
            def_name = defender.name

        def_log = ''
        stats = ''

        if isinstance(attacker, Hero):
            stats = f"attacker.info.status_all(attacker)\n"

        if def_name != attacker.name:
            def_log = ''.join([f"\n\n", def_name, f"\n", bonuses_d, debuffs_d])

        def_ = defender

        if isinstance(defender, list):
            def_ = defender[0]

        evasion_chance = def_.get_evasion(attacker)

        # log = ''.join([
        #     log,
        # ])

        log = (
            f"\n\n\n",
            f"Действие: {attacker.action} ({attacker.technique.name if attacker.action == 'Техники' else attacker.spell.name})\n",
            f"Атакующий: {attacker.name} {self.get_hp(attacker)}\n",
            f"{f'Цель: {def_name} {self.get_hp(defender)}' if def_name != attacker.name else ''}\n\n",
            # bonuses_a,
            # f"\n\n",
            # stats,
            # debuffs_a,
            f'Шанс уклонения = {formatted(evasion_chance * 100)}% '
            f'(Скорость {formatted(attacker.speed)} (attacker) vs {formatted(def_.speed)}) '
            f'(Точность {formatted(def_.accuracy)})\n'
            '/end'
        )

        log = ''.join(log)

        return log

    @staticmethod
    def get_effects(entity):
        info = HeroInfo()

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
