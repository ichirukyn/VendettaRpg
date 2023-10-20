import math

# data = {
#     "lvl": 300,
#     "exp": 0,
#     "exp_to_lvl": 814903,
#     "exp_total": 90952662,
# }

data = {
    "lvl": 1,
    "exp": 0,
    "exp_to_lvl": 50,
    "exp_total": 50,
}


class EntityLevel:
    lvl = 1
    exp_total = 0
    exp = 0
    exp_to_lvl = 50
    base_reward = 1  # Ид ранга

    def exp_reward(self, difficulty):
        reward = self.base_reward * self.lvl * math.log(self.exp_total + 1, 2)
        reward *= difficulty

        # need_battle = self.exp_to_lvl / reward
        # print('need_battle', need_battle)
        # print('reward', reward)

        return reward

    def init_level(self, data):
        self.lvl = data['lvl']
        self.exp = data['exp']
        self.exp_to_lvl = data['exp_to_lvl']
        self.exp_total = data['exp_total']

    def check_lvl_up(self):
        need_to_lvl = self.exp_to_lvl - self.exp

        if need_to_lvl <= 0:
            self.exp += 1
            return True

        return False
