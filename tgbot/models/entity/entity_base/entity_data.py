# TODO: Заготовка под разбитие основного класса
class EntityData:
    id = 0
    chat_id = 0
    team_id = 0
    is_leader = False
    class_name = ''
    race_name = ''
    class_id = 0
    race_id = 0

    def init_data(self, hero_id, chat_id, team_id, is_leader, class_name, race_name, class_id, race_id):
        self.id = hero_id
        self.chat_id = chat_id
        self.team_id = team_id
        self.is_leader = is_leader
        self.class_name = class_name
        self.race_name = race_name
        self.class_id = class_id
        self.race_id = race_id
