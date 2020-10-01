import re

from bot.bot import Bot
from bot.constants import Bot as Bot_constants

from discord import Message
from discord.ext import commands


class FilterCog(commands.Cog):
    """Cog that filters and deletes messages with offensive content."""

    def __init__(self) -> None:
        """Sets up the cog."""
        self.bad_words = re.compile(
            Bot_constants.offensive_words_regex,
            flags=re.IGNORECASE
        )

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """
        Dispatched when a message is sent.

        This is overriden to check if a message has offensive content.
        """
        await self._check_for_offensive_content(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message) -> None:
        """
        Dispatched when a message is edited.

        This is overriden to check if a message has offensive content.
        """
        await self._check_for_offensive_content(after)

    async def _check_for_offensive_content(self, message: Message) -> None:
        """Checks if the message contains offensive content."""
        if self.bad_words.search(message.content):
            # bot/cogs/moderation/message_log.py will handle this
            await message.delete()


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(FilterCog())
