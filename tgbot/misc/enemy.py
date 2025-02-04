from simulation.fetch import fetch
from simulation.generate import mob_generate
from tgbot.api.enemy import get_enemy
from tgbot.models.user import DBCommands


rank = {
    "Обычный": 1,
    "Редкий": 2,
    "Элитный": 3,
    "Легендарный": 4,
    "Миф": 5,
}

async def init_enemies(db: DBCommands, list_id, session, player_team):
    avg_lvl = sum(hero.lvl for hero in player_team)

    races, classes, _ = await fetch()

    config = []

    for id in list_id:
        enemy_db = await get_enemy(session, id)
        config.append({
            "id": id,
            "name": enemy_db.get('name'),
            "race": enemy_db.get('race_id'),
            "class": enemy_db.get('class_id'),
            "rank": rank[enemy_db.get('rank', 'Обычный')],
        })

    enemies = []

    for c in config:
        # Enemy
        enemy = await mob_generate(c, races, classes, [], session, avg_lvl)

        # Weapon
        enemy_weapon = await db.get_enemy_weapon(c.get('id'))
        weapon = await db.get_weapon(enemy_weapon.get('weapon_id', 1))

        enemy.init_weapon(weapon, enemy_weapon.get("lvl"))

        enemies.append(enemy)

    return enemies
