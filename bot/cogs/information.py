"""Information module."""

import datetime
import discord
import textwrap

from discord.ext import commands
from bot.bot import Bot


class InformationCog(commands.Cog):
    """Information cog. Has commands that shows server info and user info."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    @commands.command(name="userinfo", aliases=["user"])
    async def userinfo(self, ctx: commands.Context, member: discord.Member = None) -> None:
        """Shows information about a member."""

        if member is not None and ctx.author != member:
            for role in ctx.author.roles:
                if role.name == "Staff":
                    break
            else:
                await ctx.send(":x: **ERROR:** You may use this command only on yourself.")
                return

        member: discord.Member = ctx.author if member is None else member

        embed: discord.Embed = discord.Embed(
            title=f"{member.nick} ({member})" if member.nick is not None else f"{member}",
            color=self.bot.constants["style"]["colors"]["normal"]
        )
        embed.add_field(
            name="User information",
            value=textwrap.dedent(f"""
                Created at: {member.created_at}
                Name: {member.mention}
                ID: {member.id}
            """),
            inline=False
        )
        embed.add_field(
            name="Member information",
            value=textwrap.dedent(f"""
                Joined at: {member.joined_at}
                Roles: {", ".join(role.mention for role in member.roles if role.name != "@everyone").rstrip(",")}""")
        )
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @userinfo.error
    async def userinfo_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid member specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="serverinfo", aliases=["server"])
    async def serverinfo(self, ctx: commands.Context) -> None:
        """Shows information about the server."""

        online_members = 0
        idle_members = 0
        dnd_members = 0
        offline_members = 0
        for member in ctx.guild.members:
            if member.status.__str__() == "online": online_members += 1
            elif member.status.__str__() == "idle": idle_members += 1
            elif member.status.__str__() == "dnd": dnd_members += 1
            elif member.status.__str__() == "offline": offline_members += 1

        embed: discord.Embed = discord.Embed(
            color=self.bot.constants["style"]["colors"]["normal"]
        )
        embed.add_field(
            name="Server information",
            value=textwrap.dedent(f"""
                Created at: {ctx.guild.created_at}
                Voice region: {ctx.guild.region}
                Emotes: {len(ctx.guild.emojis)}
                Features: {", ".join(ctx.guild.features)}"""),
            inline=False
        )
        embed.add_field(
            name="Channels",
            value=textwrap.dedent(f"""
                Text channels: {len(ctx.guild.text_channels)}
                Voice channels: {len(ctx.guild.voice_channels)}"""),
            inline=False
        )
        embed.add_field(
            name="Members count",
            value=textwrap.dedent(f"""
                Members: {len(ctx.guild.members)}
                Staff members: {len(ctx.guild.get_role(self.bot.constants["server"]["staff-roles"]["ids"]["staff"]).members)}
                Trial staff members: {len(ctx.guild.get_role(self.bot.constants["server"]["staff-roles"]["ids"]["trial-staff"]).members)}"""),
            inline=False
        )
        embed.add_field(
            name="Member statuses",
            value=textwrap.dedent(f"""
                :green_circle: Online: {online_members}
                :yellow_circle: Idle: {idle_members}
                :red_circle: Do not disturb: {dnd_members}
                :black_circle: Offline: {offline_members}"""),
            inline=False
        )
        await ctx.send(embed=embed)

    @serverinfo.error
    async def serverinfo_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")


def setup(bot: Bot) -> None:
    bot.add_cog(InformationCog(bot))
