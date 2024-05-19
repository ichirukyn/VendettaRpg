from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup

from tgbot.misc.locale import keyboard
from tgbot.models.user import DBCommands


class Item:
    def __init__(self, item):
        self.id = item.get('item_id', 0)
        self.name = item.get('name', 'Name')
        self.desc = item.get('desc', '')
        self.value = item.get('value', 0)
        self.type = item.get('type', '')
        self.modify = item.get('modify', 0)
        self.is_check = False

    def get_desc(self):
        return f"*{self.name}*\n{self.desc}\n\n"

    def get_kb(self):
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"]))
        return kb


class WeaponItem(Item):
    async def check(self, db: DBCommands, hero_id):
        weapon = await db.get_hero_weapons(hero_id)

        if weapon['weapon_id'] == self.id:
            self.is_check = True

    def get_desc(self):
        return f"*{self.name}*\n{self.desc}\n• Урон — {self.value}\n\n"

    def get_kb(self):
        kb = InlineKeyboardMarkup(row_width=1)

        if self.is_check:
            kb.add(
                InlineKeyboardButton(text='Снять', callback_data='Снять'),
                InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"])
            )
        else:
            kb.add(
                InlineKeyboardButton(text='Экипировать', callback_data='Экипировать'),
                InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"])
            )
        return kb


class BookItem(Item):
    async def check(self, db: DBCommands, hero_id):
        weapon = await db.get_hero_weapons(hero_id)

        if weapon['weapon_id'] == self.id:
            self.is_check = True

    def get_kb(self):
        kb = InlineKeyboardMarkup(row_width=1)

        if self.is_check:
            kb.add(
                InlineKeyboardButton(text='Изучить', callback_data='Изучить'),
                InlineKeyboardButton(text=keyboard["back"], callback_data=keyboard["back"])
            )
        return kb

    def get_desc(self):
        return f"*{self.name}*\n{self.desc}\n\n{'Вы не можете изучить эту книгу.' if not self.is_check else ''}"


class ConsumableItem(Item):
    pass

    # def get_description(self):
    #     effects_text = '\n'.join([f"{effect['name']} - {effect['value']}%" for effect in self.effects])
    #     return f"*{self.name}*\n{self.desc}\n\n"
