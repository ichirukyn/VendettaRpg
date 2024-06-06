import logging

from tgbot.config import load_config

logger = logging.getLogger(__name__)
config = load_config(".env")

logging.basicConfig(
    level=config.logger.level,
    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)
