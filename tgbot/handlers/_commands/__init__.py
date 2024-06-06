from tgbot.handlers._commands.admins import admins
from tgbot.handlers._commands.reset.reset import reset
from tgbot.handlers._commands.start import start


def commands(dp):
    admins(dp)
    reset(dp)
    start(dp)
