import asyncio

import asyncpg

from tgbot.config import Config
from tgbot.config import load_config


async def create_pool(config: Config):
    return await asyncpg.create_pool(
        user=config.db.user,
        password=config.db.password,
        host=config.db.host,
        database=config.db.database
    )

if __name__ == '__main__':
    config = load_config(".env")

    loop = asyncio.get_event_loop()
    # loop.run_until_complete(create_db(config))
