import textwrap
from datetime import datetime

from bot.bot import Bot
from bot.constants import Channels, Colors

from discord import Embed, Member
from discord.ext import commands


class MemberLogCog(commands.Cog):
    """Has listeners that logs member joins and member leaves."""

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Listener for member joins."""
        member_information = Embed(
            title="Member joined",
            timestamp=datetime.now(),
            color=Colors.green
        )
        member_information.add_field(
            name="General information",
            value=textwrap.dedent(f"""
                Name: {member} ({member.mention})
                ID: {member.id}
                Account creation date: {member.created_at}
            """),
            inline=False
        )
        member_information.set_thumbnail(url=member.avatar_url)
        member_log_channel = member.guild.get_channel(Channels.member_logs)
        await member_log_channel.send(embed=member_information)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        """Listener for member leaves."""
        member_information = Embed(
            title="Member left",
            timestamp=datetime.now(),
            color=Colors.red
        )
        member_information.add_field(
            name="General information",
            value=textwrap.dedent(f"""
                Name: {member} ({member.mention})
                ID: {member.id}
                Account creation date: {member.created_at}
            """),
            inline=False
        )
        member_information.set_thumbnail(url=member.avatar_url)
        member_log_channel = member.guild.get_channel(Channels.member_logs)
        await member_log_channel.send(embed=member_information)


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(MemberLogCog())
