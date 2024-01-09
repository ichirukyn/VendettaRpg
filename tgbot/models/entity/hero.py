import copy

from tgbot.misc.other import formatted
from tgbot.models.entity._class import Class
from tgbot.models.entity.effect import Effect
from tgbot.models.entity.entity import Entity
from tgbot.models.entity.race import Race


class HeroFactory:
    @staticmethod
    def create_hero(id, data, stats):
        hero = {
            'entity_id': id,
            'name': data['name'],
            'rank': data['rank'],
            'money': data['money'],
            'strength': stats['strength'],
            'health': stats['health'],
            'speed': stats['speed'],
            'dexterity': stats['dexterity'],
            'accuracy': stats['accuracy'],
            'soul': stats['soul'],
            'intelligence': stats['intelligence'],
            'submission': stats['submission'],
            'crit_rate': stats['crit_rate'],
            'crit_damage': stats['crit_damage'],
            'resist': stats['resist'],
            'free_stats': stats['free_stats'],
            'chat_id': data['chat_id'],
        }
        return Hero(**hero)

    @staticmethod
    def create_init_hero(user_id, chat_id, name):
        hero = {
            'entity_id': user_id,
            'name': name,
            'rank': 'Редкий',
            'money': 5000,
            'strength': 1,
            'health': 1,
            'speed': 1,
            'dexterity': 1,
            'accuracy': 1,
            'soul': 1,
            'intelligence': 1,
            'submission': 1,
            'crit_rate': 0.05,
            'crit_damage': 0.5,
            'resist': 0.1,
            'free_stats': 20,
            'chat_id': chat_id,
        }

        return Hero(**hero)


class Hero(Entity):
    def __init__(self, entity_id, name, rank, money, strength, health, speed, dexterity, accuracy, soul, intelligence,
                 submission, crit_rate, crit_damage, resist, free_stats, chat_id):
        super().__init__(entity_id, name, rank, strength, health, speed, dexterity, accuracy, soul, intelligence,
                         submission, crit_rate, crit_damage, resist)
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
            if not isinstance(bonus, Race) and not isinstance(bonus, Class):
                bonuses += f'{bonus.name}, '

        return bonuses

    def active_debuff(self):
        debuff_list = ''

        for debuff in self.hero.debuff_list:
            debuff_list += f'{debuff.name}, '

        return debuff_list

    def status(self):
        self.hero.default_stats()
        self.hero.update_stats()
        so_string = f'• Свободные очки: `{formatted(self.hero.free_stats)}` \n'

        return (
            f"*Ваш статус:*\n"
            f"• Имя: *{self.hero.name}* \n"
            f"• ID: `{self.hero.id}`\n"
            f"• Раса: `{self.hero.race.name}`\n"
            f"     • Класс: `{self.hero._class.name}`\n"
            f"• Уровень: `{self.hero.lvl}` `({self.hero.exp_now}/{self.hero.exp_to_lvl})`\n"
            f"     • Ранг: `{self.hero.rank}`\n"
            f"• Золото: `{formatted(self.hero.money)}`\n"
            f"••••••••••••••••••••••••••••••••••••••\n"
            f"*Ваше текущее состояние:*\n"
            f"• ХП: `{formatted(self.hero.hp)} / {formatted(self.hero.hp_max)}`\n"
            f"• Мана: `{formatted(self.hero.mana)} / {formatted(self.hero.mana_max)}`\n"
            f"°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°\n"
            f"*Ваши характеристики:*\n"
            f"• Сила: `{formatted(self.hero.strength)}`\n"
            f"• Здоровье: `{formatted(self.hero.health)}`\n"
            f"• Скорость: `{formatted(self.hero.speed)}`\n"
            f"• Ловкость: `{formatted(self.hero.dexterity)}`\n"
            f"• Меткость: `{formatted(self.hero.accuracy)}`\n"
            f"• Интеллект: `{formatted(self.hero.intelligence)}`\n"
            f"• Дух: `{formatted(self.hero.soul)}`\n"
            f"• Подчинение: `{formatted(self.hero.submission)}`\n"
            f"• Крит. Шанс: `{formatted(self.hero.crit_rate * 100)}%`\n"
            f"• Крит. Урон: `{formatted(self.hero.crit_damage * 100)}%`\n"
            f"••••••••••••••••••••••••••••••••••••••\n"
            f"• Общая сила: `{formatted(self.hero.total_stats)}`\n"
            f"{so_string if self.hero.free_stats > 0 else ''}"
        )

    def status_flat(self):
        self.hero.default_stats()
        self.hero.update_stats()
        return (
            f"*Ваши характеристики без бонусов:*\n"
            f"• Сила: `{formatted(self.hero.flat_strength)}`\n"
            f"• Здоровье: `{formatted(self.hero.flat_health)}`\n"
            f"• Скорость: `{formatted(self.hero.flat_speed)}`\n"
            f"• Ловкость: `{formatted(self.hero.flat_dexterity)}`\n"
            f"• Меткость: `{formatted(self.hero.flat_accuracy)}`\n"
            f"• Интеллект: `{formatted(self.hero.flat_intelligence)}`\n"
            f"• Дух: `{formatted(self.hero.flat_soul)}`\n"
            f"• Подчинение: `{formatted(self.hero.flat_submission)}`\n"
        )

    def status_elements_damage(self):
        self.hero.default_stats()
        self.hero.update_stats()
        return (
            f"*Урон стихий:*\n"
            f"• Огонь: `{formatted(self.hero.fire_damage * 100)}%`\n"
            f"• Вода: `{formatted(self.hero.water_damage * 100)}%`\n"
            f"• Земля: `{formatted(self.hero.earth_damage * 100)}%`\n"
            f"• Воздух: `{formatted(self.hero.air_damage * 100)}%`\n"
            f"• Тьма: `{formatted(self.hero.dark_damage * 100)}%`\n"
            f"• Свет: `{formatted(self.hero.light_damage * 100)}%`\n"
        )

    def status_elements_resist(self):
        self.hero.default_stats()
        self.hero.update_stats()
        return (
            f"*Защита стихий:*\n"
            f"• Огонь: `{formatted(self.hero.fire_resist * 100)}%`\n"
            f"• Вода: `{formatted(self.hero.water_resist * 100)}%`\n"
            f"• Земля: `{formatted(self.hero.earth_resist * 100)}%`\n"
            f"• Воздух: `{formatted(self.hero.air_resist * 100)}%`\n"
            f"• Тьма: `{formatted(self.hero.dark_resist * 100)}%`\n"
            f"• Свет: `{formatted(self.hero.light_resist * 100)}%`\n"
        )

    def character_info(self, bonus):
        if bonus == 'race':
            header = (
                f"Ваша раса *{self.hero.race.name}*\n\n"
                f"• Описание: {self.hero.race.desc_short}\n"
            )

            return self.bonus_info(header, self.hero.race.bonuses, True, True, True)

        if bonus == 'class':
            header = (
                f"Ваш класс *{self.hero._class.name}*\n\n"
                f"• Описание: {self.hero._class.desc}\n"
            )

            return self.bonus_info(header, self.hero._class.bonuses, True)

    def bonus_info(self, header, bonuses, is_mod=False, is_damage=False, is_resist=False):
        elements = []
        resists = []
        others = []

        for el in bonuses:
            if '_damage' in el.attribute:
                new_el = copy.copy(el)
                new_el.value = f"{formatted(new_el.value * 100, 1)}%"
                elements.append(new_el)
                continue

            elif '_resist' in el.attribute:
                new_el = copy.copy(el)
                new_el.value = f"{formatted(new_el.value * 100, 1)}%"
                resists.append(new_el)
                continue

            if el.type == 'percent':
                new_el = copy.copy(el)
                new_el.value = f"{formatted(new_el.value * 100, 1)}%"
                others.append(new_el)
                continue

            others.append(el)

        text = header

        if is_mod and len(others) != 0:
            text += self.effects_info(others, '*Модификаторы*')

        if is_damage and len(elements) != 0:
            text += self.effects_info(elements, '*Урон стихий*')

        if is_resist and len(resists) != 0:
            text += self.effects_info(resists, '*Защита стихий*')
            text += f"°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°\n"

        return text

    @staticmethod
    def effects_info(effects: [Effect], header):
        text = f"°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°\n{header}:\n"

        # mod_text = ''
        for effect in effects:
            text += f"• {effect.name}: `{effect.value}`\n"

        return text

    def status_all(self):
        return "°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°\n" \
            .join([self.status(), self.status_elements_damage(), self.status_elements_resist()])
