class BattleState:
    def __init__(self, team_allies, team_enemies):
        self.team_allies = team_allies
        self.team_enemies = team_enemies

    @staticmethod
    def average(team, attribute):
        total = sum(getattr(member, attribute) for member in team)
        return total / len(team)

    @staticmethod
    def log(value, description):
        print(f"{description}: {value}%")

    def evaluate(self):
        # Средние уровни команды-союзников и противников
        avg_level_allies = self.average(self.team_allies, 'lvl')
        avg_level_enemies = self.average(self.team_enemies, 'lvl')
        self.log(avg_level_allies, 'Средний уровень союзников')
        self.log(avg_level_enemies, 'Средний уровень противников')

        # Среднее здоровье команды-союзников и противников
        avg_health_allies = self.average(self.team_allies, 'hp')
        avg_health_enemies = self.average(self.team_enemies, 'hp')
        self.log(avg_health_allies, 'Среднее здоровье союзников')
        self.log(avg_health_enemies, 'Среднее здоровье противников')

        # Среднее здоровье команды-союзников и противников
        avg_health_allies = self.average(self.team_allies, 'hp_max')
        avg_health_enemies = self.average(self.team_enemies, 'hp_max')
        self.log(avg_health_allies, 'Среднее максимальное здоровье союзников')
        self.log(avg_health_enemies, 'Среднее максимальное здоровье противников')

        # Среднее значение маны команды-союзников и противников
        # avg_mana_allies = self.average(self.team_allies, 'mana')
        # avg_mana_enemies = self.average(self.team_enemies, 'mana')
        # self.log(avg_mana_allies, 'Среднее значение маны союзников')
        # self.log(avg_mana_enemies, 'Среднее значение маны противников')

        # Среднее значение участников команды-союзников и противников
        avg_members_allies = len(self.team_allies)
        avg_members_enemies = len(self.team_enemies)
        self.log(avg_members_allies, 'Среднее количество участников в команде союзников')
        self.log(avg_members_enemies, 'Среднее количество участников в команде противников')

        # Среднее значение ОС участников команды-союзников и противников
        avg_stats_allies = self.average(self.team_allies, 'total_stats')
        avg_stats_enemies = self.average(self.team_enemies, 'total_stats')
        self.log(avg_stats_allies, 'Среднее значение ОС участников команды союзников')
        self.log(avg_stats_enemies, 'Среднее значение ОС участников команды противников')
