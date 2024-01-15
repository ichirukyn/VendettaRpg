class EntityStatsFactory:
    @staticmethod
    def data_formatter(stats):
        strength = stats.get('strength', 0)
        health = stats.get('health', 0)
        speed = stats.get('speed', 0)
        dexterity = stats.get('dexterity', 0)
        accuracy = stats.get('accuracy', 0)
        soul = stats.get('soul', 0)
        intelligence = stats.get('intelligence', 0)
        submission = stats.get('submission', 0)

        return strength, health, speed, dexterity, accuracy, soul, intelligence, submission


class EntityStats:
    strength = 0
    health = 0
    speed = 0
    dexterity = 0
    accuracy = 0
    soul = 0
    intelligence = 0
    submission = 0

    def init_stats(self, strength, health, speed, dexterity, accuracy, soul, intelligence, submission):
        self.strength = strength
        self.health = health
        self.speed = speed
        self.dexterity = dexterity
        self.accuracy = accuracy
        self.soul = soul
        self.intelligence = intelligence
        self.submission = submission

    def init_stats_factory(self, stats):
        self.init_stats(*EntityStatsFactory.data_formatter(stats))
