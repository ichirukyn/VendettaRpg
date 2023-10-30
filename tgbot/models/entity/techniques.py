from datetime import datetime


class Technique:
    def __init__(self, technique_id, name, desc, duration, duration_time, bonuses):
        self.technique_id = technique_id

        # TODO: Подумать о подробном описании
        self.desc = desc
        self.name = name
        self.lvl = 0

        self.bonuses = bonuses
        self.effects = []

        self.start_time = datetime.now()
        self.duration = duration
        self.duration_time = duration_time
