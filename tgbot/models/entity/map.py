from tgbot.models.entity.events import BattleEvent
from tgbot.models.entity.events import QuestEvent
from tgbot.models.entity.events import Zone


class MapFactory:
    @staticmethod
    def create_map(size_x, size_y):
        map_data = [[MapCell((x, y)) for y in range(size_y)] for x in range(size_x)]

        # Установка начальной зоны со сражением
        goblin_battle_event = BattleEvent("You hear rustling in the bushes.", "Goblin", 5)
        starting_zone = Zone("Starting Zone", events=[goblin_battle_event])
        map_data[0][0].zone = starting_zone

        # Установка второй зоны с квестом
        quest_event = QuestEvent("A villager approaches you with a quest.", "Save the captured villagers.")
        quest_zone = Zone("Quest Zone", events=[quest_event])
        map_data[1][1].zone = quest_zone

        # Установка эффектов для начальной ячейки
        map_data[0][0].effects = []

        map = Map(size_x, size_y)
        map.map_data = map_data

        return map


class Map:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.current_coordinates = (0, 0)
        self.current_direction = "up"
        self.map_data = []

    def move_forward(self):
        x, y = self.current_coordinates
        if self.current_direction == "up" and y < self.size_y - 1:
            y += 1
        elif self.current_direction == "down" and y > 0:
            y -= 1
        elif self.current_direction == "left" and x > 0:
            x -= 1
        elif self.current_direction == "right" and x < self.size_x - 1:
            x += 1

        self.current_coordinates = (x, y)

    def rotate_camera(self, direction):
        directions = ["up", "right", "down", "left"]
        current_index = directions.index(self.current_direction)
        if direction == "left":
            current_index = (current_index - 1) % 4
        elif direction == "right":
            current_index = (current_index + 1) % 4

        self.current_direction = directions[current_index]

    def update_coordinates(self, new_coordinates):
        x, y = new_coordinates
        if 0 <= x < self.size_x and 0 <= y < self.size_y:
            self.current_coordinates = new_coordinates
        else:
            print("Ошибка: Попытка перемещения за пределы карты.")

    def interact_with_current_cell(self):
        x, y = self.current_coordinates
        current_cell = self.map_data[x][y]

        # Взаимодействие с эффектами в ячейке
        for effect in current_cell.effects:
            print(f"Effect: {effect.description}")

        # Взаимодействие с событиями в ячейке
        current_cell.trigger_events()

    def enter_zone(self, hero):
        current_cell = self.map_data[hero.current_coordinates[0]][hero.current_coordinates[1]]
        if current_cell.zone:
            print(f"Entering {current_cell.zone.name}")
            for event in current_cell.zone.events:
                event.trigger(hero)

    def trigger_current_cell_effects(self, hero):
        current_cell = self.map_data[hero.current_coordinates[0]][hero.current_coordinates[1]]
        for effect in current_cell.effects:
            print(f"Encountered {effect.name}")
            effect.apply(hero)

    def display_map(self):
        for row in self.map_data:
            for cell in row:
                if cell.coordinates == self.current_coordinates:
                    print("[X]", end=" ")  # Местоположение игрока
                else:
                    print("[ ]", end=" ")  # Пустая ячейка
            print()  # Переход на новую строку


class MapCell:
    def __init__(self, coordinates, zone_type, min_level, possible_events=None, triggers=None):
        self.coordinates = coordinates
        self.zone_type = zone_type
        self.min_level = min_level

        self.possible_events = possible_events or []
        self.triggers = triggers or []

        self.player_list = []
        self.npc_list = []

    def add_player(self, player):
        self.player_list.append(player)

    def remove_player(self, player):
        if player in self.player_list:
            self.player_list.remove(player)

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def remove_npc(self, npc):
        if npc in self.npc_list:
            self.npc_list.remove(npc)


MapFactory.create_map(3, 3)
