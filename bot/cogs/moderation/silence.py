import asyncio
import logging
import textwrap
from datetime import datetime

from bot.bot import Bot
from bot.constants import Channels, Colors, Roles
from bot.converters import DurationConverter

from discord import Embed
from discord.ext import commands


logging = logging.getLogger(__name__)


class SilenceCog(commands.Cog):
    """Has commands that silences and unsilences channels."""

    def __init__(self) -> None:
        """Sets up the cog."""
        # This list will contain objects of channels that are silenced
        self._silenced_channels = []

    @commands.command(name="silence", aliases=("lock",))
    @commands.has_role(Roles.staff)
    async def silence(
        self,
        ctx: commands.Context,
        until: DurationConverter
    ) -> None:
        """Locks the channel for the specified time."""
        if ctx.channel in self._silenced_channels:
            await ctx.send(":x: This channel is already silenced.")
            return

        await self._silence(ctx, until)

    @commands.command(name="unsilence", aliases=("unlock",))
    @commands.has_role(Roles.staff)
    async def unsilence(
        self,
        ctx: commands.Context
    ) -> None:
        """Unlocks the channel, if it was locked already."""
        if ctx.channel not in self._silenced_channels:
            await ctx.send(":x: This channel is not silenced.")
            return

        await self._unsilence(ctx)

    async def _silence(self, ctx: commands.Context, until: datetime) -> None:
        """Base function for silencing a channel."""
        self._silenced_channels.append(ctx.channel)
        until_seconds = self._datetime_to_seconds(
            until
        ) - self._datetime_to_seconds(
            datetime.now()
        )
        until_minutes = until_seconds / 60
        await ctx.channel.set_permissions(
            ctx.guild.get_role(Roles.human),
            send_messages=False,
            read_messages=True,
            read_message_history=True
        )
        await ctx.send(
            ":white_check_mark: This channel is silenced for "
            f"{until_minutes:.2f} minutes."
        )
        # Save action on the #management channel
        management_channel = ctx.guild.get_channel(Channels.management)
        report = Embed(
            title="Channel silenced",
            timestamp=datetime.now(),
            color=Colors.red
        )
        report.add_field(
            name="Information",
            value=textwrap.dedent(f"""
                Channel: {ctx.channel} ({ctx.channel.mention})
                Channel ID: {ctx.channel.id}
                Moderator: {ctx.author} ({ctx.author.mention})
                Moderator ID: {ctx.author.id}
                Until: {until_minutes:.2f} minutes
            """),
            inline=False
        )
        await management_channel.send(embed=report)
        await asyncio.sleep(until_seconds)
        await self._unsilence(ctx)

    async def _unsilence(self, ctx: commands.Context) -> None:
        """Base function for unsilencing a channel."""
        if ctx.channel not in self._silenced_channels:
            return

        del self._silenced_channels[self._silenced_channels.index(ctx.channel)]

        await ctx.channel.edit(sync_permissions=True)
        await ctx.send(":white_check_mark: This channel is now unsilenced.")
        # Save action on the #management channel
        management_channel = ctx.guild.get_channel(Channels.management)
        report = Embed(
            title="Channel unsilenced",
            timestamp=datetime.now(),
            color=Colors.green
        )
        report.add_field(
            name="Information",
            value=textwrap.dedent(f"""
                Channel: {ctx.channel} ({ctx.channel.mention})
                Channel ID: {ctx.channel.id}
                Moderator: {ctx.author} ({ctx.author.mention})
                Moderator ID: {ctx.author.id}
            """),
            inline=False
        )
        await management_channel.send(embed=report)

    def _datetime_to_seconds(self, datetime_obj: datetime) -> int:
        """Converts a datetime object to seconds."""
        return int(datetime_obj.strftime("%s"))


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(SilenceCog())
