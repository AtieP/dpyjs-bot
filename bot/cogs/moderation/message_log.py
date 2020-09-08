import asyncio
import textwrap
from datetime import datetime

from bot.bot import Bot
from bot.constants import Channels, Colors

from discord import (
    Embed, Message, RawMessageDeleteEvent, RawMessageUpdateEvent
)
from discord.ext import commands


class MessageLogCog(commands.Cog):
    """Logs message deletions and message edits to assist with moderation."""

    def __init__(self, bot: Bot) -> None:
        """Sets up the cog."""
        self.bot = bot
        # When a message is deleted, both on_message_delete and
        # on_raw_message_delete are triggered, so, when on_message_delete is
        # triggered, it will save the message ID here so the message deletion
        # will be not logged twice
        self._deleted_message_ids = []
        # Same thing with on_message_edit and on_raw_message_edit
        self._edited_message_ids = []

    @commands.Cog.listener()
    async def on_message_delete(self, message: Message) -> None:
        """Listener for message deletions."""
        self._deleted_message_ids.append(message.id)
        if message.embeds:
            return
        message_logs_channel = message.guild.get_channel(Channels.message_logs)
        embed = Embed(
            title="Message deleted",
            timestamp=datetime.now(),
            color=Colors.default
        )
        embed.add_field(
            name="Information",
            value=textwrap.dedent(f"""
                Author: {message.author} ({message.author.mention})
                Author ID: {message.author.id}
                Channel: {message.channel} ({message.channel.mention})
                Channel ID: {message.channel.id}
            """),
            inline=False
        )
        embed.add_field(
            name="Message",
            value=textwrap.shorten(message.content, 1024, placeholder="..."),
            inline=False
        )
        await message_logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(
        self,
        message: RawMessageDeleteEvent
    ) -> None:
        """
        Listener for message deletions.

        Unlike `on_message_delete`, this is a raw response, so the message
        content is unknown if it wasn't cached.
        """
        # on_message_delete and on_raw_message_delete, wait 1 second and then
        # check if the deleted message also triggered on_message_delete
        await asyncio.sleep(1)
        if message.message_id in self._deleted_message_ids:
            return

        message_channel = self.bot.get_channel(message.channel_id)
        message_logs_channel = self.bot.get_channel(Channels.message_logs)

        embed = Embed(
            title="Message deleted",
            timestamp=datetime.now(),
            color=Colors.default
        )
        embed.add_field(
            name="Information",
            value=textwrap.dedent(f"""
                Channel: {message_channel} ({message_channel.mention})
                Channel ID: {message_channel.id}
                Message ID: {message.message_id}
                The author is unknown, the message is not found in the internal
                cache.
            """),
            inline=False
        )
        embed.add_field(
            name="Message",
            value=(
                "The message is unknown, the message is not found in the "
                "internal cache."
            ),
            inline=False
        )
        await message_logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message) -> None:
        """Listener for message edits."""
        self._edited_message_ids.append(after.id)
        if before.embeds or after.embeds:
            return
        message_logs_channel = after.guild.get_channel(Channels.message_logs)
        embed = Embed(
            title="Message edited",
            timestamp=datetime.now(),
            color=Colors.default
        )
        embed.add_field(
            name="Information",
            value=textwrap.dedent(f"""
                Author: {after.author} ({after.author.mention})
                Author ID: {after.author.id}
                Channel: {after.channel} ({after.channel.mention})
                Channel ID: {after.channel.id}
            """),
            inline=False
        )
        embed.add_field(
            name="Message before",
            value=textwrap.shorten(before.content, 1024, placeholder="..."),
            inline=False
        )
        embed.add_field(
            name="Message now",
            value=textwrap.shorten(after.content, 1024, placeholder="..."),
            inline=False
        )
        await message_logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, after: RawMessageUpdateEvent) -> None:
        """
        Listener for message edits.

        Unlike `on_message_edit`, this is a raw response, so the message
        content is unknown if it wasn't cached.
        """
        # on_message_edit and on_raw_message_edit are triggered at the same
        # time when a message is edited, wait 1 second and then check if
        # on_message_edit was called.
        await asyncio.sleep(1)
        if after.message_id in self._edited_message_ids:
            return
        try:
            message_content = after.data["content"]
        except KeyError:
            # It's an embed
            return
        message_channel = self.bot.get_channel(after.channel_id)
        message_logs_channel = self.bot.get_channel(Channels.message_logs)

        embed = Embed(
            title="Message edited",
            timestamp=datetime.now(),
            color=Colors.default
        )
        embed.add_field(
            name="Information",
            value=textwrap.dedent(f"""
                Channel: {message_channel} ({message_channel.mention})
                Channel ID: {message_channel.id}
                Message ID: {after.message_id}
                The author is unknown, this message is not cached.
            """),
            inline=False
        )
        embed.add_field(
            name="Message before",
            value="The message before is unknown, the message is not cached.",
            inline=False
        )
        embed.add_field(
            name="Message now",
            value=textwrap.shorten(message_content, 1024, placeholder="..."),
            inline=False
        )
        await message_logs_channel.send(embed=embed)


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(MessageLogCog(bot))
