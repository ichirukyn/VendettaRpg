# Статистика конкретного боя
from tgbot.models.helpers.DBHelper import DatabaseHelper


class StatisticBattle:
    damage = 0
    damage_max = 0
    healing = 0
    healing_max = 0
    damage_taken = 0
    damage_taken_max = 0
    block_damage = 0
    counter_strike_damage = 0

    hits_count = 0
    miss_count = 0
    crit_count = 0

    evasion_count = 0
    evasion_success_count = 0
    block_count = 0
    counter_strike_count = 0
    pass_count = 0

    kill_enemy = 0
    kill_hero = 0
    death = 0

    def get_battle_statistic(self):
        return (
            f"*Статистика игрока:*\n"
            f"• Общий урон: `{self.damage}`\n"
            f"• Максимальный урон: `{self.damage_max}`\n"
            f"\n"
            f"• Исцеление: `{self.healing}`\n"
            f"• Максимальное исцеление: `{self.healing_max}`\n"
            f"\n"
            f"• Полученный урон: `{self.damage_taken}`\n"
            f"• Максимальный полученный урон: `{self.damage_taken_max}`\n"
            f"• Заблокированный урон: `{self.block_damage}`\n"
            f"• Возвращённый урон: `{self.block_damage}`\n"
            f"\n"
            f"• Количество попаданий: `{self.hits_count}`\n"
            f"• Количество промахов: `{self.miss_count}`\n"
            f"• Количество крит. попаданий: `{self.crit_count}`\n"
            f"\n"
            f"• Количество \"Уклонений\": `{self.evasion_count}`\n"
            f"• Количество успешных \"Уклонений\": `{self.evasion_success_count}`\n"
            f"• Количество \"Защиты\": `{self.block_count}`\n"
            f"• Количество \"Контрударов\": `{self.counter_strike_count}`\n"
            f"• Количество \"Пассов\": `{self.pass_count}`\n"
            f"\n"
            f"• Убито противников: `{self.kill_enemy}`\n"
            f"• Убито героев: `{self.kill_hero}`\n"
            f"• Смертей: `{self.death}`\n"
        )

    def check_max(self, attr, val):
        current_val = self.__getattribute__(attr)

        if val > current_val:
            self.__setattr__(attr, val)


# Общая статистика игрока
class Statistic(DatabaseHelper):
    battle = StatisticBattle()

    def __init__(self):
        self.damage = 0
        self.damage_max = 0
        self.healing = 0
        self.healing_max = 0
        self.damage_taken = 0
        self.damage_taken_max = 0
        self.block_damage = 0
        self.counter_strike_damage = 0
        self.hits_count = 0
        self.miss_count = 0
        self.crit_count = 0
        self.money_all = 0
        self.money_wasted = 0
        self.evasion_count = 0
        self.evasion_success_count = 0
        self.block_count = 0
        self.counter_strike_count = 0
        self.pass_count = 0
        self.escape_count = 0
        self.win_one_to_one = 0
        self.win_team_to_team = 0
        self.lose_one_to_one = 0
        self.lose_team_to_team = 0
        self.count_one_to_one = 0
        self.count_team_to_team = 0
        self.kill_enemy = 0
        self.kill_hero = 0
        self.death = 0

    def battle_update(self, battle: StatisticBattle):
        self.damage += battle.damage
        self.healing += battle.healing
        self.damage_taken += battle.damage_taken
        self.block_damage += battle.block_damage
        self.counter_strike_damage += battle.counter_strike_damage
        self.hits_count += battle.hits_count
        self.miss_count += battle.miss_count
        self.crit_count += battle.crit_count
        self.evasion_count += battle.evasion_count
        self.evasion_success_count += battle.evasion_success_count
        self.block_count += battle.block_count
        self.counter_strike_count += battle.counter_strike_count
        self.pass_count += battle.pass_count
        self.kill_enemy += battle.kill_enemy
        self.kill_hero += battle.kill_hero
        self.death += battle.death

        self.check_max('damage_max', battle.damage_max)
        self.check_max('healing_max', battle.healing_max)
        self.check_max('damage_taken_max', battle.damage_taken_max)

    def check_max(self, attr, val):
        current_val = self.__getattribute__(attr)

        if val > current_val:
            self.__setattr__(attr, val)

    def get_statistic(self):
        return (
            f"*Статистика игрока:*\n"
            f"• Общий урон: `{self.damage}`\n"
            f"• Максимальный урон: `{self.damage_max}`\n"
            f"\n"
            f"• Исцеление: `{self.healing}`\n"
            f"• Максимальное исцеление: `{self.healing_max}`\n"
            f"\n"
            f"• Полученный урон: `{self.damage_taken}`\n"
            f"• Максимальный полученный урон: `{self.damage_taken_max}`\n"
            f"\n"
            f"• Количество крит. попаданий: `{self.crit_count}`\n"
            f"• Количество попаданий: `{self.hits_count}`\n"
            f"• Количество промахов: `{self.miss_count}`\n"
            f"\n"
            f"• Всего золота: `{self.money_all}`\n"
            f"• Всего золота потрачено: `{self.money_wasted}`\n"
            f"\n"
            f"• Количество \"Уклонений\": `{self.evasion_count}`\n"
            f"• Количество успешных \"Уклонений\": `{self.evasion_success_count}`\n"
            f"• Количество \"Защиты\": `{self.block_count}`\n"
            f"• Количество \"Контрударов\": `{self.counter_strike_count}`\n"
            f"• Количество \"Пассов\": `{self.pass_count}`\n"
            f"• Количество \"Побегов\": `{self.escape_count}`\n"
            f"\n"
            f"• Побед 1 на 1: `{self.win_one_to_one}`\n"
            f"• Побед команда на команду: `{self.win_team_to_team}`\n"
            f"• Поражений 1 на 1: `{self.lose_one_to_one}`\n"
            f"• Поражений команда на команду: `{self.lose_team_to_team}`\n"
            f"• Количество сражений 1 на 1: `{self.count_one_to_one}`\n"
            f"• Количество сражений команда на команду: `{self.count_team_to_team}`\n"
            f"\n"
            f"• Убито противников: `{self.kill_enemy}`\n"
            f"• Убито героев: `{self.kill_hero}`\n"
            f"• Смертей: `{self.death}`\n"
        )
