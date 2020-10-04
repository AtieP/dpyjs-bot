import logging
import textwrap

from bot.bot import Bot
from bot.constants import Channels, Colors, Roles

from discord import AllowedMentions, Embed
from discord.ext import commands


logger = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    """Has a listener that handles all type of errors."""

    def __init__(self, bot: Bot) -> None:
        """Sets up the cog."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.errors.CommandError
    ) -> None:
        """Handles all type of errors that happened when executing commands."""
        if hasattr(error, "handled"):
            logger.debug((
                f"Command {ctx.command} executed by {ctx.author} on"
                f"{ctx.channel} has been already handled."
            ))
            return
        if isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.UserInputError):
            await self.handle_user_input_error(ctx, error)
        elif isinstance(error, commands.errors.CommandInvokeError):
            await self.handle_some_other_error(ctx, error)

        logger.debug((
            f"{ctx.command} executed by {ctx.author} ({ctx.author.id}): "
            f"{error.__class__.__name__}: {error}"
        ))

    async def handle_user_input_error(
        self,
        ctx: commands.Context,
        error: commands.errors.UserInputError
    ) -> None:
        """Handles exceptions that have been raised due to wrong input."""
        if isinstance(error, commands.errors.ArgumentParsingError):
            await ctx.send(
                f":x: Argument parsing error: {error}"
            )
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(
                f":x: Bad argument: {error}"
            )
        elif isinstance(error, commands.errors.BadUnionArgument):
            await ctx.send(
                f":x: Bad argument: {error}"
            )
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(
                f":x: Missing required argument: {error.param.name}"
            )
        elif isinstance(error, commands.errors.TooManyArguments):
            await ctx.send(
                f":x: Too many arguments: {error}"
            )
        else:
            await ctx.send(
                ":x: Your input is wrong. Please, check it again."
            )

    async def handle_some_other_error(
        self,
        ctx: commands.Context,
        error: commands.errors.CommandInvokeError
    ) -> None:
        """Handles any other error."""
        await ctx.send(":x: Sorry, an unexpected error happened.")
        # Send error report to an internal error channel.
        errors_channel = ctx.guild.get_channel(Channels.errors)
        core_dev_role = ctx.guild.get_role(Roles.core_developers)
        core_developers_allowed_mention = AllowedMentions(
            everyone=False,
            roles=[] if not core_dev_role else [core_dev_role]
        )
        embed = Embed(
            color=Colors.red
        )
        embed.add_field(
            name="Command information",
            value=textwrap.dedent(f"""
                Cog: {ctx.cog.__class__.__name__}
                Command: {ctx.command}
            """),
            inline=False
        )
        embed.add_field(
            name="Invoker information",
            value=textwrap.dedent(f"""
                Invoker's name: {ctx.author}
                Invoker's ID: {ctx.author.id}
                Invoker's channel: {ctx.channel.mention}
                Invoker's channel ID: {ctx.channel.id}
                Invoker's message:
                ```
                {ctx.message.content}
                ```
            """),
            inline=False
        )
        embed.add_field(
            name="The error",
            value=textwrap.dedent(f"""
                ```
                {error.__class__.__name__}: {error}
                ```
            """),
            inline=False
        )
        await errors_channel.send(
            f"{'' if not core_dev_role else core_dev_role.mention}",
            allowed_mentions=core_developers_allowed_mention,
            embed=embed
        )


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(ErrorHandler(bot))
