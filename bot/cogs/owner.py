import logging
import traceback
from typing import Optional

from bot.bot import Bot
from bot.constants import Bot as Bot_constants, Colors, Roles

from discord import Embed, TextChannel
from discord.ext import commands


logger = logging.getLogger(__name__)


class OwnerCog(commands.Cog):
    """Has a group of commands for the bot's owners."""

    def __init__(self, bot: Bot) -> None:
        """Sets up the cog."""
        self.bot = bot

    @commands.group()
    async def owner(self, ctx: commands.Context) -> None:
        """A group of owner-only commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @owner.command(name="eval", aliases=("e",))
    async def eval_(self, ctx: commands.Context, *, code: str) -> None:
        """Executes code."""
        if ctx.author.id not in Bot_constants.owners:
            return

        code = code.strip("`")
        if code.startswith(("py\n", "python\n")):
            code = "\n".join(code.split("\n")[1:])

        logger.info(f"{ctx.author} is wanting to eval:\n```py\n{code}```")

        try:
            exec(
                "async def __function():\n"
                + "".join(f"\n    {line}" for line in code.split("\n")),
                locals()
            )

            await locals()["__function"]()
        except Exception:
            res = Embed(
                title="Error",
                description=f"```{traceback.format_exc()}```",
                color=Colors.red
            )
            res.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.avatar_url_as(static_format="png")
            )
            await ctx.send(embed=res)

    @owner.command(name="say")
    @commands.has_role(Roles.admins)
    async def say(
        self,
        ctx: commands.Context,
        channel: Optional[TextChannel],
        *,
        message: str
    ) -> None:
        """Returns a message to a channel."""
        channel_ = channel if channel else ctx.channel
        await channel_.send(message)

    @owner.group()
    async def reload(self, ctx: commands.Context) -> None:
        """A group of owner-only reload commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @reload.command()
    async def extension(self, ctx: commands.Context, ext: str) -> None:
        """Reloads a bot extension."""
        if ctx.author.id not in Bot_constants.owners:
            return

        try:
            self.bot.reload_extension(ext)
        except commands.errors.ExtensionNotLoaded:
            await ctx.send(f':x: Could not load extension "{ext}".')
            return

        await ctx.send(
            f':white_check_mark: Extension "{ext}" reloaded successfully.'
        )


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(OwnerCog(bot))
