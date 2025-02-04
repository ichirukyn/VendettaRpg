from aiogram.types import Message

from tgbot.models.user import DBCommands


async def bot_started(message: Message):
    db = DBCommands(message.bot.get('db'))
    session = message.bot.get('session')

    # users = await db.get_users()

    # for user in users:
    #     await message.bot.send_message(chat_id=user['chat_id'],
    #                                    text="Бот запущен, напишите /start, для перехода на главный экран..")
    # await asyncio.sleep(1)

    # with open('spell.json', encoding='utf-8') as f:
    #     spells = json.load(f)
    #
    # for spell in spells:
    #     await create_spell(spell)
    #     await asyncio.sleep(1)


def started(dp):
    dp.register_message_handler(bot_started, commands=["started"], state='*')
