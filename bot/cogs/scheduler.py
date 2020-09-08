from bot.bot import Bot

from discord.ext import commands


class Scheduler(commands.Cog):
    """Schedules expiration dates for things."""
    
    pass


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(Scheduler())
