import discord
import logging
import json
import psycopg2
import os

from discord.ext import commands


class Bot(commands.Bot):
    """The main bot class."""

    def __init__(self, *args, **kwargs) -> None:
        """Sets up the bot instance."""

        super().__init__(*args, **kwargs)

        # Load constants.
        with open("config.json", "r") as constants_file:
            self.constants = json.load(constants_file)

        self.__init_logger()

    async def on_ready(self) -> None:
        """Called when the bot has connected to Discord successfully."""

        self.logger_info(
            f"Connected to Discord as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        """Handles on_message event."""

        if message.author.bot or message.author == self.user or not message.guild:
            return

        await self.process_commands(message)

    def run(self, token: str, *args, **kwargs) -> None:
        """Connects to Discord and the PostgreSQL database."""

        self.logger_info("Connecting into the database...")

        self.database_connection = psycopg2.connect(
            dbname="dpyjs-bot-db",
            user=os.environ["DPYJS_DB_USER"],
            password=os.environ["DPYJS_DB_PASSWORD"],
            host="localhost"
        )
        self.database_cursor = self.database_connection.cursor()

        self.logger_info("Connected to database.")
        self.logger_info("Connecting into Discord...")

        super().run(token, *args, **kwargs)

    async def close(self) -> None:
        """Closes connection into Discord."""

        self.logger_info("Shutting down connection into Discord...")

        await super().close()
        self.database_cursor.close()
        self.database_connection.close()

        self.logger_info("Done. Connection to Discord has been shut down.")

    def __init_logger(self) -> None:
        """Initializes the logger. Meant for internal usage."""

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(
            filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

        self.logger.addHandler(handler)

    def logger_debug(self, msg: str, *args, **kwargs) -> None:
        """Logs a debug message."""

        self.logger.debug(msg, *args, **kwargs)

    def logger_info(self, msg: str, *args, **kwargs) -> None:
        """Logs an info message."""

        self.logger.info(msg, *args, **kwargs)

    def logger_warning(self, msg: str, *args, **kwargs) -> None:
        """Logs a warning message."""

        self.logger.warning(msg, *args, **kwargs)

    def logger_error(self, msg: str, *args, **kwargs) -> None:
        """Logs an error message."""

        self.logger.error(msg, *args, **kwargs)

    def logger_critical(self, msg: str, *args, **kwargs) -> None:
        """Logs a critical message."""

        self.logger.critical(msg, *args, **kwargs)

    def logger_exception(self, msg: str, *args, **kwargs) -> None:
        """Logs an exception message."""

        self.logger.exception(msg, *args, **kwargs)
