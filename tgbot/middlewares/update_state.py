from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from tgbot.misc.hero import init_hero
from tgbot.misc.hero import init_team
from tgbot.models.user import DBCommands

list_update = [
    # 'LocationState:home',
    # 'LocationState:tower',
    # 'TeamState',
]

list_ignore = [
    'BattleState',
    'LocationState:town',
]


def logger(id, state, message=''):
    print(f"-- {id} id - {state} -- {message}\n")


class UpdateStatsMiddleware(BaseMiddleware):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    async def on_pre_process_message(self, message: Message, data: dict):
        session = message.bot.get('session')
        db = DBCommands(message.bot.get('db'))
        dp: Dispatcher = self.kwargs['dp']

        chat_id = message.chat.id
        data = await dp.storage.get_data(chat=chat_id)

        try:
            hero = data['hero']
            state = await dp.storage.get_state(chat=chat_id)

            if state in list_ignore or state.split(':')[0] in list_ignore:
                return logger(hero.id, state, message.text)

            # Если игрок в списке "обновляемых" локаций, его состояние обновляется полностью
            if state in list_update or state.split(':')[0] in list_update:
                hero = await init_hero(db, session, hero_id=hero.id)

                # Если состоит в группе, обновить группу в state
                if hero.team_id > 0:
                    team = await db.get_team_heroes(hero.team_id)

                    player_team = await init_team(db, session, team, hero)

                    await dp.storage.update_data(chat=chat_id, player_team=player_team)
                    await dp.storage.update_data(chat=chat_id, leader_id=team[0]['leader_id'])
                else:
                    await dp.storage.update_data(chat=chat_id, player_team=[hero])

            # Иначе, обновляем только частично
            # else:
            #     hero = await init_hero(db, hero_id=hero.id)

            await dp.storage.update_data(chat=chat_id, hero=hero)
            logger(hero.id, state, message.text)

        except KeyError:
            return print('Update State Error')
