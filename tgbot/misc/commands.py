from aiogram import types


def bot_command():
    return [
        types.BotCommand(command="/start", description="Запускает бота"),
        types.BotCommand(command="/to_home", description="Вытаскивает, в теории")
    ]
