"""Owner only commands."""

import discord
from discord.ext import commands

from bot.bot import Bot


class OwnerCog(commands.Cog):
    """Owner commands Cog class."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    @commands.command(name="disconnect")
    async def disconnect(self, ctx: commands.Context) -> None:
        """Closes connection to Discord."""

        # Ensure a bot owner is executing this.
        if ctx.author.id not in self.bot.constants["bot"]["internal_perms"]:
            return

        await self.bot.close()

    @commands.command(name="reload-e", aliases=["reload-extension"])
    async def reload_extension_(self, ctx: commands.Context, extension: str) -> None:
        """Reloads an extension into the bot."""

        # Ensure a bot owner is executing this.
        if ctx.author.id not in self.bot.constants["bot"]["internal_perms"]:
            return

        try:
            self.bot.reload_extension(extension)

        except (commands.errors.ExtensionError, commands.errors.ExtensionFailed, commands.errors.ExtensionNotFound,
                commands.errors.ExtensionNotLoaded, commands.errors.ExtensionAlreadyLoaded) as e:

            await ctx.send(f"Something went wrong while reloading extension {extension}. Please, review the logs.")
            self.bot.logger_error(e)
            return

        await ctx.send(f"Extension {extension} reloaded successfully.")

    @commands.command("wipe-logs", aliases=["delete-logs", "truncate-logs"])
    async def wipe_logs(self, ctx: commands.Context) -> None:
        """Deletes the log file."""

        # Ensure a bot owner is executing this.
        if ctx.author.id not in self.bot.constants["bot"]["internal_perms"]:
            return

        with open("discord.log", "w+") as log_file:
            log_file.truncate()

        await ctx.send("Log file wiped successfully.")

    @commands.command(name="sql-eval")
    async def sql_eval(self, ctx: commands.Context, *, query: str) -> None:
        """Executes SQL code."""

        # Ensure a bot owner is executing this.
        if ctx.author.id not in self.bot.constants["bot"]["internal_perms"]:
            return

        try:
            self.bot.database_cursor.execute(query)
            row = None

            if query.startswith("select"):
                row = self.bot.database_cursor.fetchall()

            await ctx.send(row if row else "Done")

        except BaseException as e:
            await ctx.send(f":x: **FATAL ERROR:** {e}")

        finally:
            self.bot.database_connection.commit()


def setup(bot: Bot) -> None:
    bot.add_cog(OwnerCog(bot))
