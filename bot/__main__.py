import os

from discord.ext import commands
from .bot import Bot


def main() -> None:

    bot = Bot("None")
    bot.command_prefix = commands.when_mentioned_or(
        bot.constants["bot"]["prefix"])

    # Add the cogs.
    bot.load_extension("bot.cogs.antimalware")
    bot.load_extension("bot.cogs.contact")
    bot.load_extension("bot.cogs.information")
    bot.load_extension("bot.cogs.owner")
    bot.load_extension("bot.cogs.tags")
    bot.load_extension("bot.cogs.userbots")
    bot.load_extension("bot.cogs.verification")
    bot.load_extension("bot.cogs.moderation.infractions")
    bot.load_extension("bot.cogs.moderation.management")
    bot.load_extension("bot.cogs.moderation.memberlog")

    # Run the bot.
    bot.run(os.environ["DPYJS_BOT_TOKEN"])


if __name__ == "__main__":
    main()
