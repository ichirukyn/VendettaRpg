import asyncio
import logging

import aiohttp
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from sql import create_pool
from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.register import RegFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.arena import arena
from tgbot.handlers.battle.handlers import battle
from tgbot.handlers.character import character
from tgbot.handlers.fortress import fortress
from tgbot.handlers.location import location
from tgbot.handlers.register import start
from tgbot.handlers.shop import shop
from tgbot.handlers.team import team
from tgbot.handlers.tower import tower
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.update_state import UpdateStatsMiddleware
from tgbot.misc.commands import bot_command

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(UpdateStatsMiddleware(dp=dp))


def register_all_filters(dp):
    dp.filters_factory.bind(RegFilter)
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    start(dp)
    location(dp)
    register_admin(dp)

    character(dp)
    shop(dp)
    team(dp)

    arena(dp)
    tower(dp)
    fortress(dp)
    battle(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='Markdown')
    dp: Dispatcher = Dispatcher(bot, storage=storage)

    db = await create_pool(config)

    session = aiohttp.ClientSession()

    bot['config'] = config
    bot['session'] = session
    bot['db'] = db
    bot['dp'] = dp

    await bot.set_my_commands(bot_command())

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await session.close()
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
