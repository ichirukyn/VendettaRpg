from tgbot.misc.other import formatted
from tgbot.models.entity.hero import Hero


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

    def battle_action(self, attacker, defender, skill):
        action_return = {'name': attacker.action, 'target': defender, 'attacker': attacker, 'log': '⁢'}

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
                    log = f"⚔️ {attacker.name} использовал \"{attacker.technique_name}\" по {defender.name} " \
                          f"и нанес {formatted(total_damage)} урона.\n"

                else:
                    log = f"⚔️ {attacker.name} атаковал {defender.name} и нанес {formatted(total_damage)} урона.\n"

            if hp > attacker.hp:
                delta = hp - attacker.hp
                log += f'🪃 {defender.name} контратаковал на {formatted(delta)} урона.'

        # if attacker.hp <= 0:
        #     log = f"{attacker.name} побежден."

        defender.sub_action = ''

        return log

    # TODO: Расширить функцию, на проверку станов, и отрицательных эффектов
    @staticmethod
    def check_durability(entity):
        log = None

        if entity.durability <= 0:
            log = f"🌀 Стойкость {entity.name} пробита, он пропускает ход."
            entity.durability = entity.durability_max

        return log

    @staticmethod
    def escape(hero_speed, enemy_speed, success_threshold):
        if hero_speed >= enemy_speed:
            return True

        speed_ratio = enemy_speed / hero_speed

        return speed_ratio > success_threshold
