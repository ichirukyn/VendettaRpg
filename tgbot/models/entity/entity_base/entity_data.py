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

    def init_data(self, hero_id):
        self.id = hero_id
