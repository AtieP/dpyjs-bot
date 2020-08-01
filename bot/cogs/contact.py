"""
Contact module. This includes a cog, that includes a single command,
used to contact the target user via a bot.
"""

import discord
import textwrap

from discord.ext import commands
from bot.bot import Bot


class ContactCog(commands.Cog):
    """Contact cog class."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    @commands.command(name="contact")
    # TODO: Some fuckery to allow self inside decorators
    # NOTE: See PureF snippets
    # @commands.has_any_role(
    #    self.bot.constants["server"]["staff-roles"]["names"]["staff"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["moderator"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["manager"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["administrator"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["head-admins"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["owner"]
    # )
    @commands.has_role("Staff")
    async def contact(self, ctx: commands.Context, member: discord.Member, *, message: str) -> None:
        """Sends a message to a member of the guild via the bot not anonymously."""

        embed: discord.Embed = discord.Embed(
            title="Message from staff",
            description=textwrap.shorten(message, 1910, placeholder="..."),
            color=self.bot.constants["style"]["colors"]["staff_message"]
        )
        embed.set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar_url))

        try:
            await member.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f":x: **ERROR:** Could not DM {member.mention}.")
            return

        await ctx.send(f":white_check_mark: **SUCCESS:** Contacted successfully {member.mention}.")

    @contact.error
    async def contact_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handles contact error."""
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send(':x: **ERROR:** You don\'t have "Staff" role.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(":x: **ERROR:** No member or message specified.")
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(":x: **ERROR:** Invalid member specified.")
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="acontact")
    # TODO: Some fuckery to allow self inside decorators
    # NOTE: See PureF snippets
    # @commands.has_any_role(
    #    self.bot.constants["server"]["staff-roles"]["names"]["staff"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["moderator"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["manager"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["administrator"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["head-admins"],
    #    self.bot.constants["server"]["staff-roles"]["names"]["owner"]
    # )
    @commands.has_role("Staff")
    async def acontact(self, ctx: commands.Context, member: discord.Member, *, message: str) -> None:
        """Sends a message to a member of the guild via the bot anonymously."""

        embed: discord.Embed = discord.Embed(
            title="Message from staff",
            description=textwrap.shorten(message, 1910, placeholder="..."),
            color=self.bot.constants["style"]["colors"]["staff_message"]
        )
        embed.set_author(name="Staff member")

        try:
            await member.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f":x: **ERROR:** Could not DM {member.mention}.")
            return

        await ctx.send(f":white_check_mark: **SUCCESS:** Anonymously contacted {member.mention}.")

    @acontact.error
    async def acontact_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handles contact error."""
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send(':x: **ERROR:** You don\'t have "Staff" role.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(":x: **ERROR:** No member or message specified.")
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(":x: **ERROR:** Invalid member specified.")
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")


def setup(bot: Bot) -> None:
    bot.add_cog(ContactCog(bot))
