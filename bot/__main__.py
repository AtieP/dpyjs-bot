import discord
from discord.ext import commands

from .bot import Bot

def main():

    bot = Bot("None")
    bot.command_prefix = commands.when_mentioned_or(bot.constants["bot"]["prefix"])

    # Add the cogs.
    bot.load_extension("bot.cogs.tags")
    bot.load_extension("bot.cogs.owner")
    bot.load_extension("bot.cogs.userbots")
    bot.load_extension("bot.cogs.verification")
    bot.load_extension("bot.cogs.moderation.memberlog")
    bot.load_extension("bot.cogs.contact")
    bot.load_extension("bot.cogs.moderation.management")
    bot.load_extension("bot.cogs.moderation.infractions")

    # Run the bot.
    bot.run(bot.constants["bot"]["token"])

if __name__ == "__main__":
    main()