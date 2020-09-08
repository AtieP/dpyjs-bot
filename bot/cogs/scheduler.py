"""Schedules things with expirations."""

from bot.bot import Bot

from discord.ext import commands


class Scheduler(commands.Cog):
    pass


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(Scheduler())
