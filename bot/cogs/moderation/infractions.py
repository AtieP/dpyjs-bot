import logging
import textwrap
from datetime import datetime
from typing import Literal, Optional, Union

from bot.bot import Bot
from bot.constants import Colors, Roles

from discord import Embed, HTTPException, Member
from discord.ext import commands


logger = logging.getLogger(__name__)


class InfractionsCog(commands.Cog):
    """Applies and pardones infractions."""

    def __init__(self, bot: Bot) -> None:
        """Sets up the cog."""
        self.bot = bot

    async def save_infraction_into_database(
        self,
        moderator_id: int,
        bad_actor_id: int,
        action: Literal["kick", "ban", "mute", "tempban"],
        inserted_at: datetime,
        expires_at: Optional[datetime],
        reason: str
    ) -> None:
        """Saves an infraction into the database."""
        await self.bot.database_connection.execute(
            """
            INSERT INTO infractions (
                moderator_id, bad_actor_id, action, inserted_at, expires_at,
                reason
            ) VALUES (
                $1, $2, $3, $4, $5, $6
            )
            """,
            moderator_id, bad_actor_id, action, inserted_at, expires_at, reason
        )

    async def dm_bad_actor(
        self,
        ctx: commands.Context,
        bad_actor: Member,
        color: int,
        action_type: str,
        reason: str,
        expires_at: datetime = None
    ) -> None:
        """Sends a DM with an embed to the bad actor."""
        embed = Embed(
            title="Infraction applied",
            color=color
        )
        embed.add_field(
            name="Information",
            value=textwrap.dedent(f"""
                Type: {action_type}
                Reason: {reason}
                {f'Expires at: {expires_at}' if expires_at else ''}
            """),
            inline=False
        )
        try:
            await bad_actor.send(embed=embed)
        except HTTPException:
            await ctx.send(f":warning: Could not DM {bad_actor.mention}")

    def respects_role_hierarchy(
        self,
        member: Member,
        target: Member,
        bot: Member
    ) -> bool:
        """
        Returns True or False, depending if the role hierarchy is respected.
        """
        if member == target:
            return False
        if bot.top_role < target.top_role:
            return False
        if member.top_role > target.top_role:
            return True
        else:
            return False

    @commands.command(name="kick")
    @commands.has_role(Roles.moderators)
    async def kick(
        self,
        ctx: commands.Context,
        bad_actor: Member,
        *,
        reason: str = "No reason specified."
    ) -> None:
        """Applies a kick to a bad actor."""
        if not self.respects_role_hierarchy(ctx.author, bad_actor, ctx.me):
            raise commands.errors.BadArgument(
                (
                    "I cannot kick that user because you are trying to kick "
                    "yourself, or they have a higher or equal role than you "
                    "or me."
                )
            )
        await self.dm_bad_actor(ctx, bad_actor, Colors.orange, "Kick", reason)
        reason = textwrap.shorten(reason, 512, placeholder="...")
        await ctx.guild.kick(bad_actor, reason=reason)
        await self.save_infraction_into_database(
            ctx.author.id,
            bad_actor.id,
            "kick",
            datetime.now(),
            None,
            reason
        )
        await ctx.send(
            f":white_check_mark: Successfully kicked {bad_actor.mention}."
        )

    @commands.command(name="ban")
    @commands.has_role(Roles.moderators)
    async def ban(
        self,
        ctx: commands.Context,
        bad_actor: Member,
        *,
        reason: str = "No reason specified."
    ) -> None:
        """Applies a ban to a bad actor."""
        if not self.respects_role_hierarchy(ctx.author, bad_actor, ctx.me):
            raise commands.errors.BadArgument(
                (
                    "I cannot kick that user because you are trying to kick "
                    "yourself, or they have a higher or equal role than you "
                    "or me."
                )
            )
        await self.dm_bad_actor(ctx, bad_actor, Colors.red, "Ban", reason)
        reason = textwrap.shorten(reason, 512, placeholder="...")
        await ctx.guild.ban(bad_actor, reason=reason, delete_message_days=0)
        await self.save_infraction_into_database(
            ctx.author.id,
            bad_actor.id,
            "ban",
            datetime.now(),
            None,
            reason
        )
        await ctx.send(
            f":white_check_mark: Successfully banned {bad_actor.mention}."
        )


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(InfractionsCog(bot))
