class MapFactory:
    @staticmethod
    def create_map(size_x, size_y):
        map_data = [[MapCell((x, y)) for y in range(size_y)] for x in range(size_x)]

        # Установка начальной зоны со сражением
        # goblin_battle_event = BattleEvent("You hear rustling in the bushes.", "Goblin", 5)
        # starting_zone = Zone("Starting Zone", events=[goblin_battle_event])
        # map_data[0][0].zone = starting_zone
        #
        # # Установка второй зоны с квестом
        # quest_event = QuestEvent("A villager approaches you with a quest.", "Save the captured villagers.")
        # quest_zone = Zone("Quest Zone", events=[quest_event])
        # map_data[1][1].zone = quest_zone

        # Установка эффектов для начальной ячейки
        # map_data[0][0].effects = []

        map_list = [
            [['town'], ['town'], ['field'], ['field'], ['field'], ['field']],
            [['town'], ['town'], ['field'], ['field'], ['field'], ['field']],
            [['field'], ['field'], ['steppe'], ['steppe'], ['steppe'], ['steppe']],
            [['forest'], ['forest'], ['forest'], ['steppe'], ['steppe'], ['steppe']],
            [['forest'], ['forest'], ['forest'], ['forest'], ['steppe'], ['steppe']],
            [['lake'], ['lake'], ['lake'], ['forest'], ['forest'], ['forest']],
        ]

        for y, row in enumerate(map_list):
            for x, cell in enumerate(row):
                map_data[x][y].zone_type = cell[0]

        map = Map(size_x, size_y)
        map.map_data = map_data

        return map


class Map:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.current_coordinates = (0, 0)
        self.prev_coordinates = (0, 0)
        self.current_direction = "down"
        self.map_data = []
        self.directions = {
            "down": {"up": (0, 1), "down": (0, -1), "right": (-1, 0), "left": (1, 0)},
            "up": {"up": (0, -1), "down": (0, 1), "right": (1, 0), "left": (-1, 0)},
            "right": {"up": (1, 0), "down": (-1, 0), "right": (0, 1), "left": (0, -1)},
            "left": {"up": (-1, 0), "down": (1, 0), "right": (0, -1), "left": (0, 1)}
        }

    def can_move(self, x, y):
        return 0 <= x < self.size_x and 0 <= y < self.size_y
        # (self.prev_coordinates[0] != x or self.prev_coordinates[1] != y)

    def move(self, direction):
        dx, dy = self.directions[self.current_direction][direction]
        x, y = self.current_coordinates

        new_direction = self.current_direction

        if 0 <= x + dx < self.size_x and 0 <= y + dy < self.size_y:
            self.current_coordinates = (x + dx, y + dy)
            print(f"Moved {direction} to {self.current_coordinates}")
        else:
            empty_x = (self.size_x - 1) - x  # (3) 4
            empty_y = (self.size_y - 1) - y  # (0) 2

            if empty_x == 0:
                if self.can_move(x, y + 1) and self.current_direction != 'up':
                    print('Вниз (y+1)')
                    self.update_coordinate(x, y + 1)
                    new_direction = 'down'
                elif self.can_move(x, y - 1) and self.current_direction != 'down':
                    print('Верх (y-1)')
                    self.update_coordinate(x, y - 1)
                    new_direction = 'up'

                print('Край правый')

            if empty_x == self.size_x - 1:
                if self.can_move(x, y - 1) and self.current_direction != 'down':
                    print('Верх (y-1)')
                    self.update_coordinate(x, y - 1)
                    new_direction = 'up'
                elif self.can_move(x, y + 1) and self.current_direction != 'up':
                    print('Вниз (y+1)')
                    self.update_coordinate(x, y + 1)
                    new_direction = 'down'

                print('Край левый')

            if empty_y == 0:
                if self.can_move(x - 1, y) and self.current_direction != 'right':
                    print('Влево (x-1)')
                    self.update_coordinate(x - 1, y)
                    new_direction = 'left'

                elif self.can_move(x + 1, y) and self.current_direction != 'left':
                    print('Вправо (x+1)')
                    self.update_coordinate(x + 1, y)
                    new_direction = 'right'

                print('Край верхний')

            if empty_y == self.size_y - 1:
                if self.can_move(x + 1, y) and self.current_direction != 'left':
                    print('Вправо (x+1)')
                    self.update_coordinate(x + 1, y)
                    new_direction = 'right'
                elif self.can_move(x - 1, y) and self.current_direction != 'right':
                    print('Влево (x-1)')
                    self.update_coordinate(x - 1, y)
                    new_direction = 'left'

                print('Край нижний')

        self.current_direction = new_direction

        if direction in ['left', 'right']:
            self.rotate_camera(direction)

        self.prev_coordinates = (x, y)

    def update_coordinate(self, x, y):
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

    def get_zone(self):
        current_cell = self.map_data[self.current_coordinates[0]][self.current_coordinates[1]]
        if current_cell.zone_type:
            return current_cell.zone_type
        else:
            return 'Zone Error'

    def trigger_current_cell_effects(self, hero):
        current_cell = self.map_data[hero.current_coordinates[0]][hero.current_coordinates[1]]
        for effect in current_cell.effects:
            print(f"Encountered {effect.name}")
            effect.apply(hero)

    def display_map(self, dx=0, dy=0):
        display = ''

        # if (new_x, new_y) == self.current_coordinates:
        #     display += f"|*{new_x, new_y}*|"  # Местоположение игрока
        # else:
        #     display += f"|{new_x, new_y}|"  # Пустая ячейка

        for y in range(self.size_y):
            for x in range(self.size_x):
                new_x = (x + dx) % self.size_x
                new_y = (y + dy) % self.size_y
                if (new_x, new_y) == self.current_coordinates:
                    display += f"|*{new_x + new_y}*|"  # Местоположение игрока
                else:
                    display += f"|{new_x + new_y}|"  # Пустая ячейка
            display += '\n'  # Переход на новую строку

        return display


class MapCell:
    def __init__(self, coordinates, zone_type=None, min_level=None, possible_events=None, triggers=None):
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
