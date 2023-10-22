from asyncpg import Connection, UniqueViolationError


class DBCommands:
    def __init__(self, db):
        self.pool: Connection = db

        self.ADD_USER = "INSERT INTO users (chat_id, login, is_admin, is_baned, ref_id) " \
                        "VALUES ($1, $2, $3, $4, $5) RETURNING id"
        self.ADD_HERO = "INSERT INTO heroes (user_id, name, clan, race_id, class_id, rank)" \
                        " VALUES ($1, $2, $3, $4, $5, $6) RETURNING id"
        self.ADD_HERO_STATS = "INSERT INTO hero_stats (hero_id, strength, health, speed, dexterity, soul, intelligence, submission, crit_rate, crit_damage, resist, total_stats) " \
                              "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) RETURNING id"

        self.GET_RACES = "SELECT * FROM races"
        self.GET_RACE = "SELECT * FROM races WHERE id = $1"
        self.GET_RACE_CLASSES = "SELECT * FROM classes WHERE race_id = $1"
        self.GET_CLASSES = "SELECT * FROM classes"
        self.GET_CLASS = "SELECT * FROM classes WHERE id = $1"

        self.GET_USER_ID = "SELECT id FROM users WHERE chat_id = $1"
        self.GET_USER = "SELECT * FROM users WHERE id = $1"
        self.GET_USERS = "SELECT * FROM users ORDER BY id"
        self.GET_HEROES = "SELECT * FROM heroes h INNER JOIN users u ON u.id = h.user_id WHERE user_id = $1"
        self.GET_HERO_STATS = "SELECT * FROM hero_stats WHERE hero_id = $1"

        self.GET_CLANS = "SELECT * FROM clans ORDER BY id"
        self.GET_HERO_CLAN = "SELECT * FROM clans WHERE name = $1"

        self.ADD_HERO_WEAPON = "INSERT INTO hero_weapons (hero_id, weapon_id, lvl) VALUES ($1, $2, $3)"
        self.GET_WEAPONS = "SELECT * FROM items WHERE id = $1 AND type='weapon'"
        self.GET_HERO_WEAPONS = "SELECT * FROM hero_weapons WHERE hero_id = $1"
        self.DEL_HERO_WEAPONS = "DELETE FROM hero_weapons WHERE hero_id = $1"

        self.GET_ENEMY = "SELECT * FROM enemies WHERE id = $1"
        self.GET_ENEMIES = "SELECT * FROM enemies ORDER BY id"
        self.GET_ENEMIES_STATS = "SELECT * FROM enemies INNER JOIN enemy_stats es " \
                                 "ON enemies.id = es.enemy_id ORDER BY es.total_stats"
        self.GET_ENEMY_STATS = "SELECT * FROM enemies INNER JOIN enemy_stats es ON enemies.id = es.enemy_id" \
                               " WHERE enemy_id = $1"
        self.GET_ENEMY_WEAPONS = "SELECT * FROM enemy_weapons WHERE enemy_id = $1"
        self.GET_ENEMY_SKILLS = "SELECT * FROM enemy_skills es INNER JOIN skills s ON es.skill_id = s.id" \
                                " WHERE enemy_id = $1"

        self.ADD_TEAM = "INSERT INTO teams (leader_id, name, is_private) VALUES ($1, $2, $3) RETURNING id"
        self.GET_TEAM = "SELECT * FROM teams WHERE id = $1"
        self.GET_TEAMS = "SELECT * FROM teams t JOIN hero_teams ht ON t.id = ht.team_id WHERE is_private = False"
        self.GET_TEAM_HEROES = "SELECT leader_id, is_private, hero_id, team_id, is_leader, prefix, h.name " \
                               "FROM teams t JOIN hero_teams ht ON ht.team_id = t.id " \
                               "JOIN heroes h ON ht.hero_id = h.user_id AND t.id = $1"
        self.ADD_HERO_TEAM = "INSERT INTO hero_teams (hero_id, team_id, is_leader) VALUES ($1, $2, $3)"
        self.GET_HERO_TEAM = "SELECT * FROM hero_teams WHERE hero_id = $1"
        self.DEL_HERO_TEAM = "DELETE FROM hero_teams WHERE hero_id = $1"
        self.GET_ENEMY_TEAM = "SELECT * FROM enemy_teams WHERE enemy_id = $1"
        self.GET_ENEMY_TEAM_ID = "SELECT * FROM teams t INNER JOIN enemy_teams et ON et.team_id = t.id WHERE t.id = $1"

        # TODO: Убрать type="None". Нужно будет подставлять nen_type
        self.ADD_HERO_TECHNIQUE = "INSERT INTO hero_technique (hero_id, technique_id, lvl) VALUES ($1, $2, $3)"
        self.GET_TECHNIQUES = "SELECT * FROM techniques WHERE id = $1 AND type='None'"
        self.GET_HERO_TECHNIQUE = "SELECT * FROM hero_technique INNER JOIN  techniques " \
                                  "ON hero_technique.technique_id = techniques.id WHERE hero_id = $1"
        self.GET_ENEMY_TECHNIQUE = "SELECT * FROM enemy_technique e INNER JOIN techniques " \
                                   "ON e.technique_id = techniques.id WHERE enemy_id = $1"

        # TODO: Убрать type="None". Нужно будет подставлять nen_type
        self.ADD_HERO_SKILL = "INSERT INTO hero_skill (hero_id, skill_id, lvl) VALUES ($1, $2, $3)"
        self.GET_SKILL = "SELECT * FROM skills WHERE id = $1 AND nen_type='None'"
        self.GET_SKILLS = "SELECT * FROM skills WHERE nen_type='None'"
        self.GET_SKILL_BONUSES = "SELECT * FROM skill_bonuses WHERE skill_id = $1"
        self.GET_HERO_SKILLS = "SELECT * FROM hero_skill INNER JOIN  skills ON hero_skill.skill_id = skills.id" \
                               " WHERE hero_id = $1"
        self.DEL_HERO_SKILL = "DELETE FROM hero_skill WHERE hero_id = $1 AND skill_id = $2"

        # TODO: Убрать type="None". Нужно будет подставлять nen_type
        self.GET_HUNT_LOCATIONS = "SELECT * FROM hunt_locations"
        self.GET_HUNT_LOCATION_EVENTS = "SELECT * FROM hunt_events INNER JOIN hunt_location_events " \
                                        "ON hunt_events.id = hunt_location_events.event_id WHERE location_id = $1"

        self.ADD_TRADER_HERO = "INSERT INTO trader_heroes (hero_id, trader_id, item_id, item_count) " \
                               "VALUES ($1, $2, $3, $4)"
        self.GET_TRADER_ITEMS = "SELECT * FROM trader_items ti JOIN traders t " \
                                "ON ti.trader_id = t.id JOIN items i ON ti.item_id = i.id WHERE trader_id = $1"
        self.GET_TRADER_ITEM = "SELECT * FROM trader_items ti JOIN traders t " \
                               "ON ti.trader_id = t.id JOIN items i ON ti.item_id = i.id WHERE trader_id = $1 AND item_id = $2"
        self.GET_HERO_TRADER_ITEMS = "SELECT * FROM trader_heroes th JOIN traders t ON th.trader_id = t.id " \
                                     "JOIN items i ON th.item_id = i.id WHERE hero_id = $1 AND t.id = $2"

        # inventory
        self.ADD_HERO_INVENTORY = "INSERT INTO hero_inventory (hero_id, item_id, count, is_stack, is_transfer) " \
                                  "VALUES ($1, $2, $3, $4, $5);"
        self.GET_HERO_INVENTORY = "SELECT * FROM hero_inventory WHERE hero_id = $1"

        # Arena
        self.GET_ARENA_FLOORS = "SELECT * FROM arena_floors ORDER BY id"
        # self.GET_ARENA_FLOOR_ENEMIES = "SELECT * FROM arena_floors a JOIN floor_enemies fe ON a.id = fe.floor_id" \
        #                                " WHERE floor_id = $1"
        self.GET_ARENA_FLOOR_ENEMIES = "SELECT * FROM arena_floors a JOIN floor_enemies fe ON a.id = fe.floor_id" \
                                       " WHERE floor_id = $1"

        self.ADD_LVL = "INSERT INTO levels (exp_to_lvl, exp_total) VALUES ($1, $2)"
        self.GET_LVLS = "SELECT * FROM levels"
        self.GET_LVL = "SELECT * FROM levels WHERE lvl = $1"

        self.ADD_HERO_LVL = "INSERT INTO hero_levels (hero_id, lvl, exp) VALUES ($1, $2, $3)"
        self.GET_HERO_LVL = "SELECT * FROM hero_levels hl JOIN levels l ON hl.lvl = l.lvl WHERE hl.hero_id = $1"

        self.GET_HERO_LVL_BY_EXP = "SELECT MAX(t.lvl + 1) FROM (SELECT lvl FROM levels WHERE exp_total - $1 <= 0) t"
        self.GET_EXP_THIS_LVL = "SELECT $1 - exp_total FROM levels WHERE lvl = $2"

    async def add_user(self, chat_id, login, is_admin=False, is_baned=False, ref_id=1):
        command = self.ADD_USER

        try:
            # check_user = await self.pool.fetchrow(self.GET_USER, chat_id)
            #
            # if check_user:
            #     return print('Юзер уже зареган')

            record_id = await self.pool.fetchval(command, chat_id, login, is_admin, is_baned, ref_id)
            return record_id
        except UniqueViolationError:
            print('`add_user` error!!')

    async def add_lvl(self, exp_to_lvl, exp_total):
        command = self.ADD_LVL

        record_id = await self.pool.fetchval(command, exp_to_lvl, exp_total)
        return record_id

    async def add_hero_lvl(self, hero_id, lvl, exp):
        command = self.ADD_HERO_LVL

        record_id = await self.pool.fetchval(command, hero_id, lvl, exp)
        return record_id

    async def get_hero_lvl(self, hero_id):
        command = self.GET_HERO_LVL

        return await self.pool.fetchrow(command, hero_id)

    async def get_lvl(self, lvl):
        command = self.ADD_LVL

        return await self.pool.fetchrow(command, lvl)

    async def update_hero_level(self, exp, lvl, hero_id):
        command = f"UPDATE hero_levels SET exp = $1, lvl = $2 WHERE hero_id = $3"

        return await self.pool.fetchrow(command, exp, lvl, hero_id)

    async def get_hero_lvl_by_exp(self, hero_exp):
        command = self.GET_HERO_LVL_BY_EXP

        return await self.pool.fetchrow(command, hero_exp)

    async def get_exp_this_lvl(self, hero_exp_total, hero_lvl):
        command = self.GET_EXP_THIS_LVL

        return await self.pool.fetchrow(command, hero_exp_total, hero_lvl)

    # TODO: Допилить..
    async def add_hero(self, user_id, name, race_id, class_id):
        clan = None
        rank = 'Редкий'

        command = self.ADD_HERO

        try:
            record_id = await self.pool.fetchval(command, user_id, name, clan, race_id, class_id, rank)
            return record_id
        except UniqueViolationError:
            print('`add_hero` error!!')

    async def add_hero_stats(self, hero_id, hero):
        strength = hero.strength
        health = hero.health
        speed = hero.speed
        soul = hero.soul
        intelligence = hero.intelligence
        dexterity = hero.dexterity
        submission = hero.submission
        crit_rate = hero.crit_rate
        crit_damage = hero.crit_damage
        resist = hero.resist
        total_stats = hero.total_stats

        command = self.ADD_HERO_STATS

        try:
            record_id = await self.pool.fetchval(command, hero_id, strength, health, speed, dexterity, soul,
                                                 intelligence, submission, crit_rate, crit_damage, resist, total_stats)
            return record_id
        except UniqueViolationError:
            print('`add_hero_stats` error!!')

    async def add_hero_inventory(self, hero_id, item_id, count=1, is_stack=True, is_transfer=True):
        command = self.ADD_HERO_INVENTORY

        try:
            record_id = await self.pool.fetchval(command, hero_id, item_id, count, is_stack, is_transfer)
            return record_id
        except UniqueViolationError:
            print('`add_hero_inventory` error!!')

    async def get_hero_inventory(self, type, hero_id):
        command = f"SELECT * FROM hero_inventory hi INNER JOIN items ON hi.item_id = items.id  " \
                  f"WHERE hero_id = $1 AND type='{type}'"

        return await self.pool.fetch(command, hero_id)

    async def get_hero_inventory_all(self, hero_id):
        command = self.GET_HERO_INVENTORY

        return await self.pool.fetch(command, hero_id)

    async def update_hero_inventory(self, stat_name, stat_value, hero_id, item_id):
        command = f"UPDATE hero_inventory SET {stat_name} = $1 WHERE hero_id = $2 AND item_id = $3"

        return await self.pool.fetch(command, stat_value, hero_id, item_id)

    # Traders
    async def add_trader_hero(self, hero_id, item_id, trader_id=1, item_count=1):
        command = self.ADD_TRADER_HERO

        try:
            record_id = await self.pool.fetchval(command, hero_id, trader_id, item_id, item_count)
            return record_id
        except UniqueViolationError:
            print('`add_trader_hero` error!!')

    async def get_trader_items(self, trader_id=1):
        command = self.GET_TRADER_ITEMS

        return await self.pool.fetch(command, trader_id)

    async def get_trader_item(self, item_id, trader_id=1):
        command = self.GET_TRADER_ITEM

        return await self.pool.fetchrow(command, trader_id, item_id)

    async def get_hero_trader_items(self, hero_id, trader_id=1):
        command = self.GET_HERO_TRADER_ITEMS

        return await self.pool.fetch(command, hero_id, trader_id)

    async def update_trader_hero(self, stat_name, stat_value, hero_id):
        command = f"UPDATE trader_heroes SET {stat_name} = $1 WHERE hero_id = $2"

        return await self.pool.fetch(command, stat_value, hero_id)

    # Race
    async def get_races(self):
        command = self.GET_RACES
        return await self.pool.fetch(command)

    async def get_race(self, race_id):
        command = self.GET_RACE
        return await self.pool.fetchrow(command, race_id)

    async def get_race_classes(self, race_id):
        command = self.GET_RACE_CLASSES
        return await self.pool.fetch(command, race_id)

    # Classes
    async def get_classes(self):
        command = self.GET_CLASSES
        return await self.pool.fetch(command)

    async def get_class(self, class_id):
        command = self.GET_CLASS
        return await self.pool.fetchrow(command, class_id)

    # User
    async def get_user_id(self, chat_id):
        command = self.GET_USER_ID

        id = await self.pool.fetchrow(command, chat_id)
        return id

    async def get_users(self):
        command = self.GET_USERS

        return await self.pool.fetch(command)

    async def get_user(self, hero_id):
        command = self.GET_USER

        return await self.pool.fetchrow(command, hero_id)

    # Hero
    async def get_heroes(self, hero_id):
        command = self.GET_HEROES

        return await self.pool.fetchrow(command, hero_id)

    async def get_all_heroes_stats(self, stats_order='total_stats'):
        command = f"SELECT * FROM heroes h INNER JOIN hero_stats hs " \
                  f"ON h.user_id = hs.hero_id ORDER BY {stats_order} DESC"

        return await self.pool.fetch(command)

    async def get_hero_stats(self, hero_id):
        command = self.GET_HERO_STATS

        return await self.pool.fetchrow(command, hero_id)

    async def update_hero_stat(self, stat_name, stat_value, hero_id):
        command = f"UPDATE hero_stats SET {stat_name} = $1 WHERE hero_id = $2"

        return await self.pool.fetchval(command, stat_value, hero_id)

    async def update_heroes(self, stat_name, stat_value, hero_id):
        command = f"UPDATE heroes SET {stat_name} = $1 WHERE user_id = $2"

        return await self.pool.fetchval(command, stat_value, hero_id)

    # Clan
    async def get_clans(self):
        command = self.GET_CLANS

        return await self.pool.fetch(command)

    async def get_hero_clan(self, name):
        command = self.GET_HERO_CLAN

        return await self.pool.fetch(command, name)

    # Weapon
    async def add_hero_weapon(self, hero_id, weapon_id, lvl=0):
        command = self.ADD_HERO_WEAPON

        try:
            return await self.pool.fetchval(command, hero_id, weapon_id, lvl)
        except UniqueViolationError:
            print('`add_hero_weapon` error!!')

    async def get_weapon(self, weapon_id):
        command = self.GET_WEAPONS

        return await self.pool.fetchrow(command, weapon_id)

    async def get_hero_weapons(self, hero_id):
        command = self.GET_HERO_WEAPONS

        return await self.pool.fetchrow(command, hero_id)

    async def del_hero_weapons(self, hero_id):
        command = self.DEL_HERO_WEAPONS

        return await self.pool.fetchrow(command, hero_id)

    # Technique
    async def add_hero_technique(self, hero_id, technique_id, lvl=0):
        command = self.ADD_HERO_TECHNIQUE

        try:
            return await self.pool.fetchval(command, hero_id, technique_id, lvl)
        except UniqueViolationError:
            print('`add_hero_technique` error!!')

    async def get_technique(self, technique_id):
        command = self.GET_TECHNIQUES

        return await self.pool.fetchrow(command, technique_id)

    async def get_hero_techniques(self, hero_id):
        command = self.GET_HERO_TECHNIQUE

        return await self.pool.fetch(command, hero_id)

    # Teams
    async def add_team(self, leader_id, name, is_private):
        command = self.ADD_TEAM

        record_id = await self.pool.fetchrow(command, leader_id, name, is_private)
        return record_id

    async def get_team(self, team_id):
        command = self.GET_TEAM

        return await self.pool.fetchrow(command, team_id)

    async def get_teams(self):
        command = self.GET_TEAMS

        return await self.pool.fetch(command)

    async def get_hero_team(self, hero_id):
        command = self.GET_HERO_TEAM

        return await self.pool.fetchrow(command, hero_id)

    async def del_hero_team(self, hero_id):
        command = self.DEL_HERO_TEAM

        return await self.pool.fetch(command, hero_id)

    async def add_hero_team(self, hero_id, team_id, is_leader=False):
        command = self.ADD_HERO_TEAM

        return await self.pool.fetchrow(command, hero_id, team_id, is_leader)

    async def get_team_heroes(self, team_id):
        command = self.GET_TEAM_HEROES

        return await self.pool.fetch(command, team_id)

    # Skill
    async def add_hero_skill(self, hero_id, skill_id, lvl=0):
        command = self.ADD_HERO_SKILL

        try:
            return await self.pool.fetchval(command, hero_id, skill_id, lvl)
        except UniqueViolationError:
            pass

    async def del_hero_skill(self, hero_id, skill_id):
        command = self.DEL_HERO_SKILL

        return await self.pool.fetch(command, hero_id, skill_id)

    async def get_skill(self, skill_id):
        command = self.GET_SKILL

        return await self.pool.fetchrow(command, skill_id)

    async def get_skills(self):
        command = self.GET_SKILLS

        return await self.pool.fetch(command)

    async def get_skill_bonuses(self, skill_id):
        command = self.GET_SKILL_BONUSES

        return await self.pool.fetch(command, skill_id)

    async def get_hero_skills(self, hero_id):
        command = self.GET_HERO_SKILLS

        return await self.pool.fetch(command, hero_id)

    # Enemy
    async def get_enemies(self):
        command = self.GET_ENEMIES

        return await self.pool.fetch(command)

    async def get_enemy(self, enemy_id):
        command = self.GET_ENEMY

        return await self.pool.fetchrow(command, enemy_id)

    async def get_enemies_stats(self):
        command = self.GET_ENEMIES_STATS

        return await self.pool.fetch(command)

    async def get_enemy_stats(self, enemy_id):
        command = self.GET_ENEMY_STATS

        return await self.pool.fetchrow(command, enemy_id)

    async def get_enemy_weapon(self, enemy_id):
        command = self.GET_ENEMY_WEAPONS

        return await self.pool.fetchrow(command, enemy_id)

    async def get_enemy_techniques(self, enemy_id):
        command = self.GET_ENEMY_TECHNIQUE

        return await self.pool.fetchrow(command, enemy_id)

    async def get_enemy_skills(self, enemy_id):
        command = self.GET_ENEMY_SKILLS

        return await self.pool.fetch(command, enemy_id)

    async def get_enemy_team(self, enemy_id):
        command = self.GET_ENEMY_TEAM

        return await self.pool.fetchrow(command, enemy_id)

    async def get_enemy_team_id(self, enemy_id):
        command = self.GET_ENEMY_TEAM_ID

        return await self.pool.fetch(command, enemy_id)

    # Arena
    async def get_arena_floors(self):
        command = self.GET_ARENA_FLOORS

        return await self.pool.fetch(command)

    async def get_arena_floor_enemies(self, floor_id):
        command = self.GET_ARENA_FLOOR_ENEMIES

        return await self.pool.fetch(command, floor_id)

    # Hunt
    async def get_hunt_locations(self):
        command = self.GET_HUNT_LOCATIONS

        return await self.pool.fetch(command)

    async def get_hunt_location_events(self, location_id):
        command = self.GET_HUNT_LOCATION_EVENTS

        return await self.pool.fetch(command, location_id)
