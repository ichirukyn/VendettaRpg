import math


class EntityLevel:
    lvl = 1
    exp = 0
    exp_now = 0
    exp_total = 0
    exp_to_lvl = 50

    global_mod = 1  # x2, x3, x5 опыт для всех, на ивенты и т.д.

    def exp_reward(self, difficulty):
        reward = self.global_mod * self.lvl * math.log(self.exp_total + 1, 2)
        # reward = self.lvl * ()
        reward *= difficulty

        # need_battle = self.exp_to_lvl / reward
        # print('need_battle', need_battle)
        # print('reward', reward)

        return reward

    def init_level(self, data):
        self.lvl = data['lvl']  # 3 ур
        self.exp = data['exp']  # 213 - 537 --
        self.exp_to_lvl = data['exp_to_lvl']  # 324
        self.exp_total = data['exp_total']  # 537
        self.exp_now = self.exp - (self.exp_total - self.exp_to_lvl)

    def check_lvl_up(self):
        need_to_lvl = self.exp_to_lvl - self.exp

        if need_to_lvl <= 0:
            self.exp += 1
            return True

        return False
