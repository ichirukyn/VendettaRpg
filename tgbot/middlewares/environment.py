from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware, BaseMiddleware
from aiogram.types import Message, ParseMode

from tgbot.misc.hero import init_team, init_hero
from tgbot.models.user import DBCommands


class EnvironmentMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    async def pre_process(self, obj, data, *args):
        data.update(**self.kwargs)


class SetParseModeMiddleware(LifetimeControllerMiddleware):
    async def pre_process(self, obj, data, *args):
        obj.parse_mode = ParseMode.MARKDOWN_V2
        print(obj)


list_state = [
    'LocationState:home',
    'LocationState:town',
    'LocationState:tower',
    'TeamState:main',
    'TeamState:add',
    'TeamState:team_list',
    'TeamState:teammate_list',
]


class UpdateStatsMiddleware(BaseMiddleware):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    async def on_pre_process_message(self, message: Message, data: dict):
        db = DBCommands(message.bot.get('db'))
        dp: Dispatcher = self.kwargs['dp']

        chat_id = message.chat.id
        data = await dp.storage.get_data(chat=chat_id)

        try:
            hero = data['hero']
            hero = await init_hero(db, hero_id=hero.id)

            state = await dp.storage.get_state(chat=chat_id)

            logger(hero.id, state)

            if state in list_state:
                if hero.team_id > 0:
                    team = await db.get_team_heroes(hero.team_id)

                    player_team = await init_team(db, team, hero)

                    await dp.storage.update_data(chat=chat_id, player_team=player_team)
                    await dp.storage.update_data(chat=chat_id, leader_id=team[0]['leader_id'])
                else:
                    await dp.storage.update_data(chat=chat_id, player_team=[hero])

                await dp.storage.update_data(chat=chat_id, hero=hero)

        except KeyError:
            return


def logger(id, state, message=''):
    print(f"{id} id - {state} -- {message}\n")
