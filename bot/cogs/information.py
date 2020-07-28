"""Information module."""

import discord
import typing as t
import textwrap

from discord.ext import commands
from bot.bot import Bot

class InformationCog(commands.Cog):
    """Information cog. Has commands that shows server info and user info."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    @commands.command(name="user")
    async def user(self, ctx: commands.Context, member: discord.Member = None) -> None:
        """Shows information about a member."""

        member: discord.Member = ctx.author if member is None else member

        embed: discord.Embed = discord.Embed(
            title=f"{member.nick} ({member})" if member.nick is not None else f"{member}",
            color=self.bot.constants["style"]["colors"]["normal"]
        )
        embed.add_field(name="User information", value=textwrap.dedent("""
            """))
