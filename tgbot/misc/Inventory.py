from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.models.user import DBCommands


class Item:
    def __init__(self, item):
        self.id = item['item_id']
        self.name = item['name']
        self.desc = item['desc']
        self.value = item['value']
        self.type = item['type']
        self.modify = item['modify']


class WeaponItem(Item):
    def __init__(self, item):
        super().__init__(item)
        self.is_equip = False

    async def check_is_equip(self, db: DBCommands, hero_id):
        weapon = await db.get_hero_weapons(hero_id)

        if weapon['weapon_id'] == self.id:
            self.is_equip = True

    def inventory(self):
        text = f"Рюкзак вмещает предметы необходимые в путешествии.\n" \
               f"{self.name}\n{self.desc}\nУрон — {self.value}\n\n"
        kb = InlineKeyboardMarkup(row_width=1)

        if self.is_equip:
            kb.add(
                InlineKeyboardButton(text='Снять', callback_data='Снять'),
                InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад')
            )
        else:
            kb.add(
                InlineKeyboardButton(text='Экипировать', callback_data='Экипировать'),
                InlineKeyboardButton(text='🔙 Назад', callback_data='🔙 Назад')
            )

        return {
            'text': text,
            'kb': kb
        }


class ConsumableItem(Item):
    def get_description(self):
        # effects_text = '\n'.join([f"{effect['name']} - {effect['value']}%" for effect in self.effects])
        return f"{self.name}\n{self.desc}\n\n"

# weapon = WeaponItem("Меч", "Мощный меч", 20)
# consumable = ConsumableItem("Зелье здоровья", "Восстанавливает здоровье", [{"name": "Здоровье", "value": 30}])
#
# print(weapon.get_description())
# print(consumable.get_description())
