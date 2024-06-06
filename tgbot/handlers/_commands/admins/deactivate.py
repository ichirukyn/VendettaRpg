from aiogram.types import Message

from tgbot.models.user import DBCommands


async def bot_deactivate(message: Message):
    bot = message.bot.get('db')

    db = DBCommands(message.bot.get('db'))
    users = await db.get_users()

    for user in users:
        try:
            await bot.send_message(user.get('chat_id'), "Бот будет отключен через несколько минут.")
        except Exception as e:
            print(e)


def deactivate(dp):
    dp.register_message_handler(bot_deactivate, commands=["deactivate"], state='*')
