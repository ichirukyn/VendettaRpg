from tgbot.misc.other import formatted
from tgbot.models.entity.entity import Entity


class HeroFactory:
    @staticmethod
    def create_hero(data, stats, race, _class):
        hero = {
            'entity_id': data['id'],
            'name': data['name'],
            'rank': data['rank'],
            'money': data['money'],
            'strength': stats['strength'],
            'health': stats['health'],
            'speed': stats['speed'],
            'dexterity': stats['dexterity'],
            'soul': stats['soul'],
            'intelligence': stats['intelligence'],
            'submission': stats['submission'],
            'crit_rate': stats['crit_rate'],
            'crit_damage': stats['crit_damage'],
            'resist': stats['resist'],
            'free_stats': stats['free_stats'],
            'chat_id': data['chat_id'],
            'race_id': race['id'],
            'class_id': _class['id'],
            'race_name': race['name'],
            'class_name': _class['name'],
        }
        return Hero(**hero)

    @staticmethod
    def create_init_hero(user_id, chat_id, name, race_id, class_id):
        hero = {
            'entity_id': user_id,
            'name': name,
            'rank': 'Редкий',
            'money': 5000,
            'strength': 1,
            'health': 1,
            'speed': 1,
            'dexterity': 1,
            'soul': 1,
            'intelligence': 1,
            'submission': 1,
            'crit_rate': 0.05,
            'crit_damage': 0.5,
            'resist': 0.1,
            'free_stats': 20,
            'chat_id': chat_id,
            'race_id': race_id,
            'class_id': class_id,
            'race_name': '',
            'class_name': '',
        }

        return Hero(**hero)


class Hero(Entity):
    def __init__(self, entity_id, name, rank, money, strength, health, speed, dexterity, soul, intelligence, submission,
                 crit_rate, crit_damage, resist, free_stats, chat_id, race_id, class_id, race_name, class_name):
        super().__init__(entity_id, name, rank, strength, health, speed, dexterity, soul, intelligence, submission,
                         crit_rate, crit_damage, resist, race_id, class_id, race_name, class_name)
        self.chat_id = chat_id
        self.info = HeroInfo(self)

        self.money = money
        self.free_stats = free_stats

    def level_up(self):
        self.free_stats += 10  # TODO: Обновить под ранги, а не статика


class HeroInfo:
    def __init__(self, hero):
        self.hero = hero

    def equip_stat(self):
        return (
            f"Оружие: {self.hero.weapon_name} {f'{self.hero.weapon_lvl} ур.' if self.hero.weapon_lvl > 0 else ''} \n"
            f"Описание: {self.hero.weapon_desc}\n"
            f"\n"
            f"Урон: {self.hero.weapon_damage}\n"
        )

    def active_bonuses(self):
        bonuses = ''

        for bonus in self.hero.active_bonuses:
            bonuses += f'{bonus.name}, '

        return bonuses

    def status(self):
        self.hero.update_stats()

    def status_begin(self):
        self.hero.update_stats()
        return (
            f"Это ваш профиль, ниже вы можете увидеть все статистики вашего персонажа.\n"
            f"■■■■■■■■■■■■■■■\n"
            f"Имя: **{self.hero.name}** (`{self.hero.id}`)\n"
            f"Ранг: {self.hero.rank}\n"
            f"Раса: {self.hero.race_name}\n"
            f"Класс: {self.hero.class_name}\n"
            f"Золото: {formatted(self.hero.money)}\n"
            f"Уровень: {self.hero.lvl} ({self.hero.exp_now}/{self.hero.exp_to_lvl})\n"
            f"□□□□□□□□□□□□□□□\n"
            f"ХП: `{formatted(self.hero.hp)} / {formatted(self.hero.hp_max)}`\n"
            f"Мана: `{formatted(self.hero.mana)}`\n"
            f"□□□□□□□□□□□□□□□\n"
            f"Сила: `{formatted(self.hero.strength)}`\n"
            f"Здоровье: `{formatted(self.hero.health)}`\n"
            f"Скорость: `{formatted(self.hero.speed)}`\n"
            f"Ловкость: `{formatted(self.hero.dexterity)}`\n"
            f"Интеллект: `{formatted(self.hero.intelligence)}`\n"
            f"Дух: `{formatted(self.hero.soul)}`\n"
            f"Подчинение: `{formatted(self.hero.submission)}`\n"
            f"Крит. Шанс: `{self.hero.crit_rate * 100}%`\n"
            f"Крит. Урон: `{self.hero.crit_damage * 100}%`\n"
            f"■■■■■■■■■■■■■■■\n"
            f"Общая сила: `{formatted(self.hero.total_stats)}`\n"
            f"{f'Свободные очки: `{formatted(self.hero.free_stats)}`' if self.hero.free_stats > 0 else ''}\n"
        )
