class EntityAggression:
    aggression = 0  # Итоговые очки агро
    aggression_base = 0  # Базовые очки
    aggression_combo = 1  # Насколько увеличивается сила агро, за счёт последовательных действий или АоЕ атак
    aggression_mod = 1  # Насколько увеличивается сила агро (для скилов воинов)
    aggression_decay = 0.9  # Коэффициент снижения агро со временем

    def default_aggression(self):
        self.aggression = self.aggression_base * self.aggression_mod

    # Обновляем агро в зависимости от урона, исцеления, контроля толпы и модификатора агро
    def update_aggression(self, damage, healing, cc):
        self.aggression += damage * self.aggression_combo
        self.aggression += healing * self.aggression_combo * 0.5
        self.aggression += cc * self.aggression_combo * 0.5
        self.aggression_mod += 1

    # Снижаем агро со временем
    def decay_aggression(self, dt):
        self.aggression *= self.aggression_decay
        self.aggression_mod = 1

    # Возвращаем итоговые очки агро
    def get_aggression(self):
        return self.aggression_base * self.aggression_mod
