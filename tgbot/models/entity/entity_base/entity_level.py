from tgbot.misc.utils import spread


class EntityLevel:
    lvl = 1
    exp = 0
    exp_now = 0
    exp_total = 0
    exp_to_lvl = 50

    # Скорость возрастания уровня, рекомендуется 1.50-1.70,
    coefficient = 1.1
    # Скорость возрастания уровня, рекомендуется 3-5,
    mod = 4
    # x2, x3, x5 опыт для всех, на ивенты и т.д.
    global_mod = 1

    def exp_reward(self, difficulty, enemy_lvl):
        # reward = self.global_mod * self.lvl * math.log(self.exp_total + 1, 2)
        reward = (self.mod * enemy_lvl) ** self.coefficient
        reward *= self.global_mod
        reward *= difficulty
        reward = spread(reward, 0.1)

        return round(reward)

    def init_level(self, data):
        self.lvl = data['lvl']
        self.exp = data['exp']
        self.exp_to_lvl = data['level']['exp_to_lvl']
        self.exp_total = data['level']['exp_total']
        self.exp_now = self.exp - (self.exp_total - self.exp_to_lvl)
        return self.exp_now

    def check_lvl_up(self):
        need_to_lvl = self.exp_to_lvl - self.exp_now

        if need_to_lvl <= 0:
            self.exp += 1
            return True

        return False
