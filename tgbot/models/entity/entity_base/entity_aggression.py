class EntityAggression:
    aggression = 0  # Итоговые очки агро
    aggression_base = 0  # Базовые очки
    aggression_combo = 1  # Насколько увеличивается сила агро, за счёт последовательных действий или АоЕ атак
    aggression_mod = 1  # Насколько увеличивается сила агро (для скилов воинов)
    aggression_decay = 0.8  # Коэффициент снижения агро со временем
    aggression_prev = 0

    def default_aggression(self):
        self.aggression = self.aggression_base * self.aggression_mod

    # Обновляем агро в зависимости от урона, исцеления, контроля толпы и модификатора агро
    def update_aggression(self, damage=1, healing=1, cc=1):
        self.aggression_prev = self.aggression

        if damage > 1:
            self.aggression += damage * self.aggression_combo

        if healing > 1:
            self.aggression += healing * self.aggression_combo * 0.5

        if cc > 1:
            self.aggression += cc * self.aggression_combo * 0.5

        if self.aggression > self.aggression_prev:
            self.aggression_combo += 0.5
        else:
            self.aggression_combo = 1

    # Снижаем агро со временем
    def decay_aggression(self):
        self.aggression *= self.aggression_decay

    # Возвращаем итоговые очки агро
    def get_aggression(self):
        return self.aggression * self.aggression_mod
