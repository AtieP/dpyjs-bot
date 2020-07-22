"""Management module."""

import datetime
import discord
import typing as t

from discord.ext import commands
from bot.bot import Bot

class ManagementCog(commands.Cog):
    """This cog contains management commands."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    @commands.command(name="infractions", aliases=["infrs"])
    @commands.has_role("Staff")
    async def infractions(self, ctx: commands.Context, user: t.Union[int, discord.Member]) -> None:
        """Shows all infractions of a user."""

        self.bot.database_cursor.execute(
            "SELECT infraction_id FROM INFRACTIONS WHERE infractor_id = %s",
            (user if isinstance(user, int) else user.id,)
        )

        row = self.bot.database_cursor.fetchall()
        self.bot.database_connection.commit()

        embed: discord.Embed = discord.Embed(
            title="Infractions",
            description=f"Infractions for <@{user if isinstance(user, int) else user.id}> (ID: {user if isinstance(user, int) else user.id})",
            color=self.bot.constants["style"]["colors"]["normal"]
        )
        embed.add_field(name="Infraction count", value=len(row), inline=False)
        embed.add_field(name="Infraction IDs", value=','.join(str(infr_id) for infr_id in row), inline=False)
        await ctx.send(embed=embed)

    @infractions.error
    async def infractions_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send(':x: **ERROR:** You don\'t have "Staff" role.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** You missed the user parameter.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid user specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="infraction", aliases=["infr"])
    @commands.has_role("Staff")
    async def infraction(self, ctx: commands.Context, infr_id: int) -> None:
        """Shows information about an infraction."""

        self.bot.database_cursor.execute(
            "SELECT * FROM infractions WHERE infraction_id = %s",
            (infr_id,)
        )

        row = self.bot.database_cursor.fetchone()
        self.bot.database_connection.commit()

        if not row:
            await ctx.send(f":x: **ERROR:** Could not find infraction **#{infr_id}**.")
            return

        embed: discord.Embed = discord.Embed(
            title=f"Infraction #{infr_id}",
            color=self.bot.constants["style"]["colors"]["normal"]
        )
        embed.add_field(name="Type", value=row[3], inline=False)
        embed.add_field(name="Hidden", value=row[5], inline=False)
        embed.add_field(name="Infractor", value=f"<@{row[2]}>", inline=False)
        embed.add_field(name="Infractor ID", value=str(row[2]), inline=False)
        embed.add_field(name="Moderator", value=f"<@{row[1]}>", inline=False)
        embed.add_field(name="Moderator ID", value=str(row[1]), inline=False)
        embed.add_field(name="Inserted at", value=row[6], inline=False)
        embed.add_field(name="Expires at", value="N/A" if not row[7] else row[7], inline=False)
        embed.add_field(name="Reason", value=row[4], inline=False)
        await ctx.send(embed=embed)

    @infraction.error
    async def infraction_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send(':x: **ERROR:** You don\'t have "Staff" role.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** You missed the infraction ID parameter.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid infraction ID specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")


def setup(bot: Bot) -> None:
    bot.add_cog(ManagementCog(bot))