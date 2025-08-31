import copy

from simulation import base_technique
from tgbot.misc.other import formatted
from tgbot.models.entity._class import Class
from tgbot.models.entity.effects.effect import Effect
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
            'strength': stats.get('strength', 1),
            'health': stats.get('health', 1),
            'speed': stats.get('speed', 1),
            'dexterity': stats.get('dexterity', 1),
            'accuracy': stats.get('accuracy', 1),
            'soul': stats.get('soul', 1),
            'intelligence': stats.get('intelligence', 1),
            'submission': stats.get('submission', 1),
            'crit_rate': stats.get('crit_rate', 1),
            'crit_damage': stats.get('crit_damage', 1),
            'resist': stats.get('resist', 1),
            'free_stats': stats.get('free_stats', 0),
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
        self.info = HeroInfo()

        self.money = money
        self.free_stats = free_stats

    def level_up(self):
        self.free_stats += 10  # TODO: Обновить под ранги, а не статика



class HeroInfo:
    @staticmethod
    def equip_stat(hero):
        return (
            f"Оружие: *{hero.weapon_name}* {f'({hero.weapon_lvl} ур.)' if hero.weapon_lvl > 0 else ''} \n"
            f"Описание: {hero.weapon_desc}\n"
            f"\n"
            f"• Урон: {formatted(hero.weapon_damage)}\n"
        )

    @staticmethod
    def active_bonuses(hero):
        bonuses = ''
        ignore_list = [Race, Class]  # Skill, Technique, etc..

        for bonus in hero.active_bonuses:
            if not any(isinstance(bonus, ignored_class) for ignored_class in ignore_list):
                bonuses += f'`{bonus.name}, `'

        if bonuses != '':
            bonuses = f'`— Эффекты —`\n{bonuses}\n'

        return bonuses

    @staticmethod
    def active_debuff(hero):
        debuff_list = ''

        for debuff in hero.debuff_list:
            debuff_list += f'`{debuff.get("name")}, `'

        if debuff_list != '':
            debuff_list = f'`— Дебаффы —`\n{debuff_list}\n'

        return debuff_list

    @staticmethod
    def dps(hero):
        return hero.damage_demo(base_technique)

        # TODO: На будущее придумать как бы удобно смотреть примерный урон за бой
        # for technique in hero.techniques:
        #     damage, _ = hero.damage_demo(technique)
        #     cd = technique.cooldown
        #     count = len(hero.techniques)




    def status(self, hero, crit=False):
        hero.update_all_stats()
        hero.default_stats()
        hero.update_regen()
        # so_string = f'`• Свободные очки: {formatted(hero.free_stats)}` \n'
        crit_string = ''

        if crit:
            crit_string += f"`• Крит. Шанс: {formatted(hero.crit_rate * 100)}%`\n"
            crit_string += f"`• Крит. Урон: {formatted(hero.crit_damage * 100)}%`\n"

        return (
            f"*Ваш статус:*\n"
            f"`• Имя: {hero.name}`\n"
            f"`• ID: {hero.id}`\n"
            f"`• Раса: {hero.race.name}`\n"
            f"     `• Класс: {hero._class.name}`\n"
            f"`• Уровень: {hero.lvl}` `({hero.exp_now}/{hero.exp_to_lvl})`\n"
            f"     `• Ранг: {hero.rank}`\n"
            # f"`• Золото: {formatted(hero.money)}`\n"
            f"`———————————————————`\n"
            f"*Ваше текущее состояние:*\n"
            f"`• ХП: {formatted(hero.hp)} / {formatted(hero.hp_max)}`\n"
            f"`• Мана: {formatted(hero.mana)} / {formatted(hero.mana_max)} ({formatted(hero.mana_reg)})`\n"
            f"`• Ки: {formatted(hero.qi)} / {formatted(hero.qi_max)} ({formatted(hero.qi_reg)})`\n"
            f"`———————————————————`\n"
            f"*Ваши характеристики:*\n"
            f"`• Сила: {formatted(hero.strength)}`\n"
            f"`• Здоровье: {formatted(hero.health)}`\n"
            f"`• Скорость: {formatted(hero.speed)}`\n"
            f"`• Ловкость: {formatted(hero.dexterity)}`\n"
            f"`• Меткость: {formatted(hero.accuracy)}`\n"
            f"`• Интеллект: {formatted(hero.intelligence)}`\n"
            f"`• Дух: {formatted(hero.soul)}`\n"
            f"`• Подчинение: {formatted(hero.submission)}`\n"
            f"`• Контроль маны: {formatted(hero.control_mana)} ({formatted(hero.control_mana_normalize * 100)}%)`\n"
            f"`• Контроль ки: {formatted(hero.control_qi)} ({formatted(hero.control_qi_normalize * 100)}%)`\n"
            f"{crit_string}"
            f"`———————————————————`\n"
            f"`• Общая сила: {formatted(hero.total_stats_flat)} ({formatted(hero.total_stats)})`\n"
            # f"{so_string if hero.free_stats > 0 else ''}"
            # f"`———————————————————`\n"
            f"`• Оружие: {hero.weapon_name} {f'({hero.weapon_lvl} ур.)' if hero.weapon_lvl > 0 else ''} - {formatted(hero.weapon_damage)} урон`\n"
            f"`• Средний урон: {self.dps(hero)}`\n"
            # f"`———————————————————`\n"
            # f"{so_string if hero.free_stats > 0 else ''}"
        )

    @staticmethod
    def status_stats(hero):
        hero.update_all_stats()
        hero.default_stats()
        hero.update_regen()
        return (
            f"*Ваше текущее состояние:*\n"
            f"`• ХП: {formatted(hero.hp)} / {formatted(hero.hp_max)}`\n"
            f"`• Мана: {formatted(hero.mana)} / {formatted(hero.mana_max)} ({formatted(hero.mana_reg)})`\n"
            f"`• Ки: {formatted(hero.qi)} / {formatted(hero.qi_max)} ({formatted(hero.qi_reg)})`\n"
            f"`———————————————————`\n"
            f"*Ваши характеристики:*\n"
            f"`• Сила: {formatted(hero.strength)}`\n"
            f"`• Здоровье: {formatted(hero.health)}`\n"
            f"`• Скорость: {formatted(hero.speed)}`\n"
            f"`• Ловкость: {formatted(hero.dexterity)}`\n"
            f"`• Меткость: {formatted(hero.accuracy)}`\n"
            f"`• Интеллект: {formatted(hero.intelligence)}`\n"
            f"`• Дух: {formatted(hero.soul)}`\n"
            f"`• Подчинение: {formatted(hero.submission)}`\n"
            f"`- Урон: {formatted(hero.weapon_damage)}`\n"
        )

    @staticmethod
    def status_flat(hero):
        hero.default_stats()
        hero.update_all_stats()
        return (
            f"*Ваши характеристики без бонусов:*\n"
            f"`• Сила: {formatted(hero.flat_strength)}`\n"
            f"`• Здоровье: {formatted(hero.flat_health)}`\n"
            f"`• Скорость: {formatted(hero.flat_speed)}`\n"
            f"`• Ловкость: {formatted(hero.flat_dexterity)}`\n"
            f"`• Меткость: {formatted(hero.flat_accuracy)}`\n"
            f"`• Интеллект: {formatted(hero.flat_intelligence)}`\n"
            f"`• Дух: {formatted(hero.flat_soul)}`\n"
            f"`• Подчинение: {formatted(hero.flat_submission)}`\n"
        )

    @staticmethod
    def status_elements_damage(hero):
        hero.default_stats()
        hero.update_all_stats()
        return (
            f"*Урон стихий:*\n"
            f"`• Огонь: {formatted(hero.fire_damage * 100)}%`\n"
            f"`• Вода: {formatted(hero.water_damage * 100)}%`\n"
            f"`• Земля: {formatted(hero.earth_damage * 100)}%`\n"
            f"`• Воздух: {formatted(hero.air_damage * 100)}%`\n"
            f"`• Тьма: {formatted(hero.dark_damage * 100)}%`\n"
            f"`• Свет: {formatted(hero.light_damage * 100)}%`\n"
        )

    @staticmethod
    def status_elements_resist(hero):
        hero.default_stats()
        hero.update_all_stats()
        return (
            f"*Защита стихий:*\n"
            f"`• Огонь: {formatted(hero.fire_resist * 100)}%`\n"
            f"`• Вода: {formatted(hero.water_resist * 100)}%`\n"
            f"`• Земля: {formatted(hero.earth_resist * 100)}%`\n"
            f"`• Воздух: {formatted(hero.air_resist * 100)}%`\n"
            f"`• Тьма: {formatted(hero.dark_resist * 100)}%`\n"
            f"`• Свет: {formatted(hero.light_resist * 100)}%`\n"
        )

    def character_info(self, hero, bonus):
        if bonus == 'race':
            header = (
                f"Ваша раса *{hero.race.name}*\n\n"
                f"• Описание: {hero.race.desc_short}\n"
            )

            return self.bonus_info(header, hero.race.bonuses, True, True, True)

        if bonus == 'class':
            header = (
                f"Ваш класс *{hero._class.name}*\n\n"
                f"• Описание: {hero._class.desc}\n"
            )

            return self.bonus_info(header, hero._class.bonuses, True)

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

            if el.type == 'percent' or isinstance(el.value, float):
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
            text += f"`———————————————————`\n"

        return text

    @staticmethod
    def effects_info(effects: [Effect], header):
        text = f"`———————————————————`\n{header}:\n"

        # mod_text = ''
        for effect in effects:
            text += f"`• {effect.name}: {effect.value}`\n"

        return text

    def status_all(self, hero):
        return "`———————————————————`\n" \
            .join([self.status(hero, True), self.status_elements_damage(hero), self.status_elements_resist(hero)])
