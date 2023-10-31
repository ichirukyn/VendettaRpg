from tgbot.misc.other import formatted
from tgbot.models.entity.entity import Entity


class HeroFactory:
    @staticmethod
    def create_hero(id, data, stats, _class):
        hero = {
            'entity_id': id,
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
            'class_id': _class['id'],
            'class_name': _class['name'],
        }
        return Hero(**hero)

    @staticmethod
    def create_init_hero(user_id, chat_id, name, class_id):
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
            'class_id': class_id,
            'class_name': '',
        }

        return Hero(**hero)


class Hero(Entity):
    def __init__(self, entity_id, name, rank, money, strength, health, speed, dexterity, soul, intelligence, submission,
                 crit_rate, crit_damage, resist, free_stats, chat_id, class_id, class_name):
        super().__init__(entity_id, name, rank, strength, health, speed, dexterity, soul, intelligence, submission,
                         crit_rate, crit_damage, resist, class_id, class_name)
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
        so_string = f'• Свободные очки: `{formatted(self.hero.free_stats)}` \n'

        return (
            f"**Ваш статус:**\n"
            f"• Имя: **{self.hero.name}** \n"
            f"• ID: `{self.hero.id}`\n"
            f"• Раса: `{self.hero.race.race_name}`\n"
            f"     • Класс: `{self.hero.class_name}`\n"
            f"• Уровень: `{self.hero.lvl}` `({self.hero.exp_now}/{self.hero.exp_to_lvl})`\n"
            f"     • Ранг: `{self.hero.rank}`\n"
            f"• Золото: `{formatted(self.hero.money)}`\n"
            f"••••••••••••••••••••••••••••••••••••••\n"
            f"**Ваше текущее состояние:**\n"
            f"• ХП: `{formatted(self.hero.hp)} / {formatted(self.hero.hp_max)}`\n"
            f"• Мана: `{formatted(self.hero.mana)}`\n"
            f"°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°\n"
            f"**Ваши характеристики:**\n"
            f"• Сила: `{formatted(self.hero.strength)}`\n"
            f"• Здоровье: `{formatted(self.hero.health)}`\n"
            f"• Скорость: `{formatted(self.hero.speed)}`\n"
            f"• Ловкость: `{formatted(self.hero.dexterity)}`\n"
            f"• Интеллект: `{formatted(self.hero.intelligence)}`\n"
            f"• Дух: `{formatted(self.hero.soul)}`\n"
            f"• Подчинение: `{formatted(self.hero.submission)}`\n"
            f"• Крит. Шанс: `{self.hero.crit_rate * 100}%`\n"
            f"• Крит. Урон: `{self.hero.crit_damage * 100}%`\n"
            f"••••••••••••••••••••••••••••••••••••••\n"
            f"• Общая сила: `{formatted(self.hero.total_stats)}`\n"
            f"{so_string if self.hero.free_stats > 0 else ''}"
        )

    def status_flat(self):
        self.hero.update_stats()
        return (
            f"**Ваши характеристики без бонусов:**\n"
            f"• Сила: `{formatted(self.hero.flat_strength)}`\n"
            f"• Здоровье: `{formatted(self.hero.flat_health)}`\n"
            f"• Скорость: `{formatted(self.hero.flat_speed)}`\n"
            f"• Ловкость: `{formatted(self.hero.flat_dexterity)}`\n"
            f"• Интеллект: `{formatted(self.hero.flat_intelligence)}`\n"
            f"• Дух: `{formatted(self.hero.flat_soul)}`\n"
            f"• Подчинение: `{formatted(self.hero.flat_submission)}`\n"
        )

    def status_elements_damage(self):
        self.hero.update_stats()
        return (
            f"**Урон стихий:**\n"
            f"• Огонь: `{formatted(self.hero.fire_damage * 100)}%`\n"
            f"• Вода: `{formatted(self.hero.water_damage * 100)}%`\n"
            f"• Земля: `{formatted(self.hero.earth_damage * 100)}%`\n"
            f"• Воздух: `{formatted(self.hero.air_damage * 100)}%`\n"
            f"• Тьма: `{formatted(self.hero.light_damage * 100)}%`\n"
            f"• Свет: `{formatted(self.hero.dark_damage * 100)}%`\n"
        )

    def status_elements_resist(self):
        self.hero.update_stats()
        return (
            f"**Защита стихий:**\n"
            f"• Огонь: `{formatted(self.hero.fire_resist * 100)}%`\n"
            f"• Вода: `{formatted(self.hero.water_resist * 100)}%`\n"
            f"• Земля: `{formatted(self.hero.earth_resist * 100)}%`\n"
            f"• Воздух: `{formatted(self.hero.air_resist * 100)}%`\n"
            f"• Тьма: `{formatted(self.hero.light_resist * 100)}%`\n"
            f"• Свет: `{formatted(self.hero.dark_resist * 100)}%`\n"
        )

    def status_all(self):
        return "°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°\n" \
            .join([self.status(), self.status_elements_damage(), self.status_elements_resist()])
