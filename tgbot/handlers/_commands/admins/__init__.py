from tgbot.handlers._commands.admins.deactivate import deactivate
from tgbot.handlers._commands.admins.started import started


def admins(dp):
    started(dp)
    deactivate(dp)
