from tgbot.handlers._commands.start.auth import auth
from tgbot.handlers._commands.start.register import register


def start(dp):
    auth(dp)
    register(dp)
