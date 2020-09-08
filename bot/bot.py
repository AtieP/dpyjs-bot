import logging

import asyncpg

from bot import constants

from discord import Message
from discord.ext import commands

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    """Represents the community's Discord Bot."""

    async def on_ready(self) -> None:
        """Called when the bot has successfully connected to Discord."""
        # Set up database connection
        self.database_connection = await asyncpg.connect(
            constants.Bot.database_url
        )

    async def on_message(self, message: Message) -> None:
        """
        Listener for messages.

        Checks if the message is sent on a guild and the message starts with
        the prefix.
        """
        if not message.guild:
            return
        if not message.content.startswith(constants.Bot.prefix):
            return

        await self.process_commands(message)

    def load_extension(self, extension: str) -> None:
        """
        Loads an extension.

        The only reason this method exists is to log what extension was
        loaded.
        """
        super().load_extension(extension)
        logger.info(f"Extension loaded: {extension}")
