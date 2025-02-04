from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from tgbot.models.user import DBCommands


class RegFilter(BoundFilter):
    key = 'is_reg'

    def __init__(self, is_reg: bool = None):
        self.is_reg = is_reg

    async def check(self, obj: Message):
        if self.is_reg is None:
            return False

        database = DBCommands(obj.bot.get('db'))

        chat_id = obj.chat.id
        user_id = await database.get_user_id(chat_id)

        # print(f"user_id: {user_id}")

        if user_id is not None:
            return self.is_reg == True

        return self.is_reg == False
