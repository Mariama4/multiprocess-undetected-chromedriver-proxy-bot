from loguru import logger
import sys

logger.remove()

# logger.add(sys.stdout)

logger.add(
    'logs/log.log',
    enqueue=True,
    format='{time:MMMM D, YYYY > HH:mm:ss} | {level} | {extra[classname]}:{extra[url]} | {message}',
    backtrace=True,
    diagnose=True
)

logger.add(
    sys.stdout,
    enqueue=True,
    format='<m>{time:MMMM D, YYYY > HH:mm:ss}</m> | ' +
           '<level>{level}</level> | ' +
           '<r>{extra[classname]}</r>:<c>{extra[url]}</c> | ' +
           '<b>{message}</b>',
    colorize=True,
    backtrace=True,
    diagnose=True
)

logger.configure(extra={'classname': 'None',
                        'url': '...'})
