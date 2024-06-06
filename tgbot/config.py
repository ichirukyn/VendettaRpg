from dataclasses import dataclass

from environs import Env
from environs import EnvError


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class RedisConfig:
    host: str
    use_redis: bool


@dataclass
class Logger:
    level: str = 'INFO'


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    is_dev: bool


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    redis: RedisConfig
    logger: Logger


def load_config(path: str = None):
    env = Env()

    try:
        env.read_env(path)
    except EnvError as e:
        raise RuntimeError(f"Error reading .env file: {e}")

    env.read_env(path)

    try:
        tg_bot = TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            is_dev=env.bool("BOT_IS_DEV"),
        )
        redis = RedisConfig(
            use_redis=env.bool("REDIS_USE"),
            host=env.str("REDIS_HOST")
        )
        db = DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        )
        # Для необязательных переменных используем env.get и default=[any], чтобы предотвратить ошибки при их отсутствии
        # misc = Miscellaneous(
        #     other_params=env.get("OTHER_PARAMS", default=None)
        # )
        logger = Logger(
            level=env.str('LOGGER_LVL')
        )
    except EnvError as e:
        raise RuntimeError(f"Missing or invalid environment variable: {e}")

    # return Config(tg_bot=tg_bot, redis=redis, db=db, misc=misc, logger=logger)
    return Config(tg_bot=tg_bot, redis=redis, db=db, logger=logger)
