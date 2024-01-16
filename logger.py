from loguru import logger

logger.add(
    'logs/log.log',
    enqueue=True
)
