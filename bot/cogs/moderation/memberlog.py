"""Member logging."""

import discord
import datetime

from discord.ext import commands
from bot.bot import Bot

class ModLogCog(commands.Cog):
    """Member logging cog."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Logs member join."""

        self.bot.database_cursor.execute(
            """
            INSERT INTO member_joins (user_id, join_date)
            VALUES (%s, %s);""",
            (member.id, str(datetime.datetime.now()))
        )

        self.bot.database_connection.commit()

        # Check if the user who joined is a user bot.
        self.bot.database_cursor.execute(
            "SELECT * FROM user_bots WHERE bot_id = %s",
            (member.id,)
        )

        row = self.bot.database_cursor.fetchone()

        if row:
            await member.add_roles(member.guild.get_role(self.bot.constants["server"]["bot-roles"]["ids"]["bot-testers"]))

        mod_log_channel: discord.TextChannel = self.bot.get_channel(self.bot.constants["server"]["text-channels"]["staff"]["mod-logs-admin"])
        if not mod_log_channel: return

        embed: discord.Embed = discord.Embed(
            title="Member joined",
            color=self.bot.constants["style"]["colors"]["member_join_color"]
        )
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="Member ID", value=str(member.id), inline=False)
        embed.add_field(name="Bot?", value="Yes" if member.bot else "No")
        embed.set_thumbnail(url=member.avatar_url)
        await mod_log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Logs member leave."""

        self.bot.database_cursor.execute(
            """
            INSERT INTO member_removes (user_id, leave_date)
            VALUES (%s, %s)""",
            (member.id, str(datetime.datetime.now()))
        )

        self.bot.database_connection.commit()

        # Check if the user who left is the owner of a user bot.
        self.bot.database_cursor.execute(
            "SELECT * FROM user_bots WHERE owner_id = %s",
            (member.id,)
        )

        row = self.bot.database_cursor.fetchone()

        # If so, kick the user bot and delete bot submission.
        if row:
            await member.guild.get_member(row[1]).kick(reason="Owner left")
            self.bot.database_cursor.execute(
                "DELECT FROM user_bots WHERE owner_id = %s",
                (member.id,)
            )
            self.bot.database_cursor.commit()

        mod_log_channel: discord.TextChannel = self.bot.get_channel(self.bot.constants["server"]["text-channels"]["staff"]["mod-logs-admin"])
        if not mod_log_channel: return

        embed: discord.Embed = discord.Embed(
            title="Member left",
            color=self.bot.constants["style"]["colors"]["member_remove_color"]
        )
        embed.add_field(name="Member", value=str(member), inline=False)
        embed.add_field(name="Member ID", value=str(member.id), inline=False)
        embed.add_field(name="Bot?", value="Yes" if member.bot else "No")
        embed.set_thumbnail(url=member.avatar_url)
        await mod_log_channel.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(ModLogCog(bot))
