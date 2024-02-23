from aiogram.types import BotCommand


def bot_command():
    return [
        BotCommand(command="/start", description="Запускает бота"),
        BotCommand(command="/to_home", description="Возвращает в главное меню"),
        BotCommand(command="/reset", description="Сбросить текущие характеристики в свободные (Только на время теста)"),
        # BotCommand(command="/help", description="Помощь по игре"),
        # BotCommand(command="/faq", description="Ответы на часто задаваемые вопросы")
    ]
