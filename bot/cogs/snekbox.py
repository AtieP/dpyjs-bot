import aiohttp

from bot.bot import Bot
from bot.constants import Bot as Bot_constants

from discord import AllowedMentions
from discord.ext import commands


class SnekboxCog(commands.Cog):
    """Has a command that executes third-party code safely."""

    @commands.command(name="eval", aliases=("e",))
    async def eval(self, ctx: commands.Context, *, code: str) -> None:
        """Evaluates Python code safely. Powered by Snekbox."""
        code = code.strip("`")
        if code.startswith(("py\n", "python\n")):
            code = "\n".join(code.split("\n")[1:])

        async with aiohttp.ClientSession() as session:
            async with session.post(
                Bot_constants.snekbox_url,
                json={
                    "input": code
                }
            ) as result:
                output = (await result.json())["stdout"]
                status_code = (await result.json())["returncode"]

        lines = output.split("\n")
        output = "\n".join(
            line for number, line in enumerate(lines) if number < 10
        )
        output = output[:1850]

        await ctx.send(
            content=(
                f"{ctx.author.mention} "
                f"Your code exited with status code {status_code}.\n"
                f"Result:\n"
                f"```\n"
                f"{output}"
                f"```"
            ),
            allowed_mentions=AllowedMentions(
                everyone=False, roles=False, users=False
            )
        )


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(SnekboxCog())
