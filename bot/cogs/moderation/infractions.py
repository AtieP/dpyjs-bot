"""Infractions module."""

import datetime
import discord
import textwrap
import typing as t

from discord.ext import commands
from bot.bot import Bot


class Infractions(commands.Cog):
    """Applies and pardones infractions."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    async def save_infraction_into_modlog_channel(
        self,
        moderator: discord.Member,
        infractor: t.Union[discord.Member, discord.User],
        action_type: str,
        reason: t.Union[str, None],
        inserted_at: datetime.datetime.now,
        expires_at: t.Union[datetime.datetime.now, None]
    ) -> None:
        """Logs an infraction into the mod-log channel."""

        mod_log_channel: discord.TextChannel = self.bot.get_channel(self.bot.constants["server"]["text-channels"]["staff"]["mod-logs-admin"])
        if not mod_log_channel: return

        embed: discord.Embed = discord.Embed(
            title="Infraction",
            color=self.bot.constants["style"]["colors"]["normal"]
        )

        embed.add_field(name="Type", value=action_type, inline=False)
        embed.add_field(name="Infractor", value=f"<@{infractor.id}>", inline=False)
        embed.add_field(name="Infractor ID", value=str(infractor.id), inline=False)
        embed.add_field(name="Moderator", value=f"<@{moderator.id}>", inline=False)
        embed.add_field(name="Moderator ID", value=str(moderator.id), inline=False)
        embed.add_field(name="Inserted at", value=datetime.datetime.fromtimestamp(expires_at) if isinstance(inserted_at, type(datetime.datetime.now)) else inserted_at, inline=False)
        embed.add_field(name="Expires at", value=datetime.datetime.fromtimestamp(expires_at) if isinstance(expires_at, type(datetime.datetime.now)) else expires_at, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)

        await mod_log_channel.send(embed=embed)

    def save_infraction_into_db(
        self,
        moderator: discord.Member,
        infractor: t.Union[discord.Member, discord.User],
        action_type: str,
        reason: t.Union[str, None],
        hidden: bool,
        inserted_at: datetime.datetime.now,
        expires_at: t.Union[datetime.datetime.now, None],
        active: bool
    ) -> None:
        """This function saves an infraction on the database."""

        if len(reason) > 512: raise ValueError("Reason musn't be longer than 512 chars.")

        self.bot.database_cursor.execute(
            """
            INSERT INTO infractions (
            moderator_id, infractor_id, action_type, reason, hidden, inserted_at, expires_at, active)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (moderator.id, infractor.id, action_type, reason, hidden, str(inserted_at),
            str(expires_at) if expires_at else None, active)
        )

        self.bot.database_connection.commit()

    @commands.command(name="kick", aliases=["k"])
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: t.Optional[str] = None):
        """Applies a kick to the specifed user."""

        if ctx.author.top_role <= member.top_role and ctx.author == member:
            await ctx.send(":x: **ERROR:** You can only kick people with a role below than yours. Also, you can't kick youself.")
            return

        elif ctx.author.top_role <= member.top_role:
            await ctx.send(":x: **ERROR:** You can only kick people with a role below than yours.")
            return

        if ctx.me.top_role <= member.top_role and ctx.author == member:
            await ctx.send(":x: **ERROR:** I can't kick a member that has a higher or equal role than mine. Also, you can't kick youself.")
            return

        elif ctx.me.top_role <= member.top_role:
            await ctx.send(":x: **ERROR:** I can't kick a member that has a higher or equal role than mine.")
            return

        if not reason: reason = "No reason specified."
        reason = textwrap.shorten(reason, 512, placeholder="...")

        # Send a message to the offender.
        try:
            embed: discord.Embed = discord.Embed(
                title="Infraction applied",
                color=self.bot.constants["style"]["colors"]["member_kick_color"]
            )
            embed.add_field(name="Action", value="Kick", inline=False)
            embed.add_field(name="Expiry", value="Right now", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            await member.send(embed=embed)

        except discord.Forbidden:
            pass

        await member.kick(reason=reason)

        self.save_infraction_into_db(
            ctx.author,
            member,
            "kick",
            reason,
            False,
            datetime.datetime.now(),
            None,
            False
        )

        await self.save_infraction_into_modlog_channel(
            ctx.author,
            member,
            "Kick",
            reason,
            datetime.datetime.now(),
            "Right now"
        )

        await ctx.send(f":white_check_mark: **SUCCESS:** Kicked {member.mention} for: {reason}")

    @kick.error
    async def kick_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(':x: **ERROR:** You don\'t have "kick members" permission.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** No member specified.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid member specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="shadowkick", aliases=["skick", "sk", "shadowk"])
    @commands.has_guild_permissions(kick_members=True)
    async def shadowkick(self, ctx: commands.Context, member: discord.Member, *, reason: t.Optional[str] = None) -> None:
        """Kicks the specified member silently, without notifying him."""

        if ctx.author.top_role <= member.top_role and ctx.author == member:
            await ctx.send(":x: **ERROR:** You can only shadow-kick people with a role below than yours. Also, you can't shadow-kick youself.")
            return

        elif ctx.author.top_role <= member.top_role:
            await ctx.send(":x: **ERROR:** You can only shadow-kick people with a role below than yours.")
            return

        if ctx.me.top_role <= member.top_role and ctx.author == member:
            await ctx.send(":x: **ERROR:** I can't shadow-kick a member that has a higher or equal role than mine. Also, you can't shadow-kick youself.")
            return

        elif ctx.me.top_role <= member.top_role:
            await ctx.send(":x: **ERROR:** I can't shadow-kick a member that has a higher or equal role than mine.")
            return

        if not reason: reason = "No reason specified."
        reason = textwrap.shorten(reason, 512, placeholder="...")

        await member.kick(reason=reason)

        self.save_infraction_into_db(
            ctx.author,
            member,
            "kick",
            reason,
            True,
            datetime.datetime.now(),
            None,
            False
        )

        await self.save_infraction_into_modlog_channel(
            ctx.author,
            member,
            "Shadow kick",
            reason,
            datetime.datetime.now(),
            "Right now"
        )

        await ctx.send(f":white_check_mark: **SUCCESS:** Shadow-kicked {member.mention} for: {reason}")

    @shadowkick.error
    async def shadowkick_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(':x: **ERROR:** You don\'t have "kick members" permission.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** No member specified.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid member specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="ban", aliases=["b"])
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: t.Optional[str] = None) -> None:
        """Bans a member permanently from the server."""

        if ctx.author.top_role <= member.top_role and ctx.author == member:
            await ctx.send(":x: **ERROR:** You can only ban people with a role below than yours. Also, you can't ban youself.")
            return

        elif ctx.author.top_role <= member.top_role:
            await ctx.send(":x: **ERROR:** You can only ban people with a role below than yours.")
            return

        if ctx.me.top_role <= member.top_role and ctx.author == member:
            await ctx.send(":x: **ERROR:** I can't ban a member that has a higher or equal role than mine. Also, you can't ban youself.")
            return

        elif ctx.me.top_role <= member.top_role:
            await ctx.send(":x: **ERROR:** I can't ban a member that has a higher or equal role than mine.")
            return

        if not reason: reason = "No reason specified."
        reason = textwrap.shorten(reason, 512, placeholder="...")

        # Send a message to the offender.
        try:
            embed: discord.Embed = discord.Embed(
                title="Infraction applied",
                color=self.bot.constants["style"]["colors"]["member_ban_color"]
            )
            embed.add_field(name="Action", value="Permanent ban", inline=False)
            embed.add_field(name="Expiry", value="N/A", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            await member.send(embed=embed)

        except discord.Forbidden:
            pass

        await member.ban(reason=reason, delete_message_days=0)

        self.save_infraction_into_db(
            ctx.author,
            member,
            "ban",
            reason,
            False,
            datetime.datetime.now(),
            None,
            True
        )

        await self.save_infraction_into_modlog_channel(
            ctx.author,
            member,
            "Ban",
            reason,
            datetime.datetime.now(),
            "N/A"
        )

        await ctx.send(f":white_check_mark: **SUCCESS:** Permanently banned {member.mention} for: {reason}")

    @ban.error
    async def ban_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(':x: **ERROR:** You don\'t have "ban members" permission.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** No member specified.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid member specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="shadowban", aliases=["shadowb", "sban", "sb"])
    @commands.has_guild_permissions(ban_members=True)
    async def shadowban(self, ctx: commands.Context, member: discord.Member, *, reason: t.Optional[str] = None) -> None:
        """Bans a member permanently from the server, without notifying the infracted user."""

        if ctx.author.top_role <= member.top_role and ctx.author == member:
            await ctx.send(":x: **ERROR:** You can only shadow-ban people with a role below than yours. Also, you can't shadow-ban youself.")
            return

        elif ctx.author.top_role <= member.top_role:
            await ctx.send(":x: **ERROR:** You can only shadow-ban people with a role below than yours.")
            return

        if ctx.me.top_role <= member.top_role and ctx.author == member:
            await ctx.send(":x: **ERROR:** I can't shadow-ban a member that has a higher or equal role than mine. Also, you can't ban youself.")
            return

        elif ctx.me.top_role <= member.top_role:
            await ctx.send(":x: **ERROR:** I can't shadow-ban a member that has a higher or equal role than mine.")
            return

        if not reason: reason = "No reason specified."
        reason = textwrap.shorten(reason, 512, placeholder="...")

        await member.ban(reason=reason, delete_message_days=0)

        self.save_infraction_into_db(
            ctx.author,
            member,
            "ban",
            reason,
            True,
            datetime.datetime.now(),
            None,
            True
        )

        await self.save_infraction_into_modlog_channel(
            ctx.author,
            member,
            "Shadow ban",
            reason,
            datetime.datetime.now(),
            "N/A"
        )

        await ctx.send(f":white_check_mark: **SUCCESS:** Permanently shadow-banned {member.mention} for: {reason}")

    @shadowban.error
    async def shadowban_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(':x: **ERROR:** You don\'t have "ban members" permission.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** No member specified.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid member specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="hackban", aliases=["hb"])
    @commands.has_guild_permissions(ban_members=True)
    async def hackban(self, ctx: commands.Context, member: int, *, reason: t.Optional[str] = None) -> None:
        """Bans a member that isn't on the server."""

        member = discord.Object(id=member)

        if member.id == ctx.author.id:
            await ctx.send(":x: **ERROR:** You can't hackban yourself.")
            return

        member_in_server = False

        for m in ctx.guild.members:
            if m.id == member.id:
                member_in_server = True
                break

        if member_in_server:
            await ctx.send(":x: **ERROR:** The member is on the server. Hint: use `ban` command.")
            return

        if not reason: reason = "No reason specified."

        await ctx.guild.ban(member, reason=textwrap.shorten(reason, 512, placeholder="..."), delete_message_days=0)

        self.save_infraction_into_db(
            ctx.author,
            member,
            "ban",
            reason,
            True,
            datetime.datetime.now(),
            None,
            True
        )

        await self.save_infraction_into_modlog_channel(
            ctx.author,
            member,
            "Ban",
            reason,
            datetime.datetime.now(),
            "N/A"
        )

        await ctx.send(f":white_check_mark: **SUCCESS:** Permanently banned {member.id} for: {reason}")

    @hackban.error
    async def hackban_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(':x: **ERROR:** You don\'t have "ban members" permission.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** No member specified.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid member specified. Hint: did you specify an ID?')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

def setup(bot: Bot) -> None:
    bot.add_cog(Infractions(bot))
