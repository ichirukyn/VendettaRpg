class Zone:
    def __init__(self, name, events=None, effects=None):
        self.name = name
        self.events = events if events else []
        self.effects = effects if effects else []


class Event:
    def __init__(self, name, description, rewards=None, hidden=False):
        self.name = name
        self.description = description
        self.rewards = rewards or []
        self.hidden = hidden
        self.triggers = []

    def add_trigger(self, trigger):
        self.triggers.append(trigger)

    def start_condition(self, player):
        # Метод для проверки начальных условий события
        pass

    def check_triggers(self, player):
        # Метод для проверки триггеров
        pass

    def complete_condition(self, player):
        # Метод для проверки завершающих условий события
        pass

    def give_rewards(self, player):
        # Метод для выдачи наград
        pass


class BattleEvent(Event):
    def __init__(self, name, description, rewards=None, hidden=False):
        super().__init__(name, description, rewards, hidden)
        self.enemies = []

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def start_battle(self):
        # Метод для начала боя
        pass


class QuestEvent(Event):
    def __init__(self, name, description, rewards=None, hidden=False):
        super().__init__(name, description, rewards, hidden)
        # Дополнительные атрибуты для квестов, если потребуется
        pass


class BossEvent(Event):
    def __init__(self, name, description, rewards=None, hidden=False):
        super().__init__(name, description, rewards, hidden)
        self.boss = None
        self.enemies = []
        self.mini_bosses = []
        self.boss_movement = False

    def add_mini_boss(self, mini_boss):
        self.mini_bosses.append(mini_boss)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def boss_visible(self):
        # Метод для проверки отображения босса на карте
        pass

    def start_boss_battle(self):
        # Метод для начала боя с боссом
        pass

    def move_boss(self):
        # Метод для перемещения босса
        pass

    def open_next_floor(self):
        # Метод для открытия следующего этажа
        pass


class Trigger:
    def __init__(self, event_id, trigger_type, name, description, text=None,
                 condition=None, condition_value=None, chance=None, reward=None,
                 mandatory=False, hidden=False):
        self.event_id = event_id
        self.trigger_type = trigger_type
        self.name = name
        self.description = description
        self.text = text
        self.condition = condition
        self.condition_value = condition_value
        self.chance = chance
        self.reward = reward
        self.mandatory = mandatory
        self.hidden = hidden
        self.completed = False

    def check_start_condition(self, player):
        # Метод для проверки начальных условий триггера
        pass

    def check_condition(self, player):
        # Метод для проверки условий триггера
        pass

    def check_chance(self):
        # Метод для проверки шанса срабатывания триггера
        pass

    def give_info(self):
        # Метод для выдачи информации по триггеру
        pass

    def complete_trigger(self):
        # Метод для завершения работы триггера
        pass
