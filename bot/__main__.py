import logging
import sys

from bot import constants
from bot.bot import Bot

import coloredlogs

from discord import AllowedMentions


# Set up the logger
root_logger = logging.getLogger()
format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

# Set up the log levels for various other loggers
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)

coloredlogs.DEFAULT_LOG_LEVEL = logging.DEBUG
coloredlogs.DEFAULT_LOG_FORMAT = format
coloredlogs.install(logger=root_logger, stream=sys.stdout)

bot = Bot(
    command_prefix=constants.Bot.prefix,
    allowed_mentions=AllowedMentions(
        everyone=False,
        users=True,
        roles=False
    )
)

bot.load_extension("bot.cogs.antivirus")
bot.load_extension("bot.cogs.error_handler")
bot.load_extension("bot.cogs.information")
bot.load_extension("bot.cogs.owner")
bot.load_extension("bot.cogs.snekbox")
bot.load_extension("bot.cogs.tags")

bot.load_extension("bot.cogs.moderation.infractions")
bot.load_extension("bot.cogs.moderation.member_log")
bot.load_extension("bot.cogs.moderation.message_log")
bot.load_extension("bot.cogs.moderation.silence")

bot.run(constants.Bot.token)
