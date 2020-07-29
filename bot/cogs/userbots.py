"""User bots (custom bots) management."""

import asyncio
import discord
import textwrap
import typing as t

from discord.ext import commands
from bot.bot import Bot


class UserbotsCog(commands.Cog):
    """The main class for the user bot management."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    @commands.command(name="submit")
    async def submit(self, ctx: commands.Context, bot_id: str, *, description: str) -> None:
        """Command to submit a request to add your bot."""

        if ctx.channel.id != self.bot.constants["server"]["text-channels"]["public"]["submit-a-bot"]:
            await ctx.message.delete()
            bot_reply: discord.Message = await ctx.send(f'{ctx.author.mention}, you use this command at <#{self.bot.constants["server"]["text-channels"]["public"]["submit-a-bot"]}>.')
            await asyncio.sleep(5)
            await bot_reply.delete()

        bot_submits_mod_channel = self.bot.get_channel(
            self.bot.constants["server"]["text-channels"]["staff"]["bot-submits"])

        if not bot_submits_mod_channel:
            await ctx.send(f':x: **FATAL ERROR:** Could not locate channel {self.bot.constants["server"]["text-channels"]["staff"]["bot-submits"]}. Please, contact the moderation team as soon as possible.')
            return

        valid_bot_id: int

        try:
            valid_bot_id = int(bot_id)

        except ValueError:
            await ctx.message.delete()
            await ctx.send(f":x: **ERROR:** {ctx.author.mention}, that is not a valid bot ID!")
            return

        await ctx.message.delete()

        # Check if that bot already exists on the database.
        self.bot.database_cursor.execute(
            "SELECT accepted, reviewed FROM user_bots WHERE bot_id = %s",
            (valid_bot_id,)
        )

        row = self.bot.database_cursor.fetchone()
        self.bot.database_connection.commit()

        if row:
            if row[0] is True:
                await ctx.send(f":x: **ERROR:** {ctx.author.mention}, that bot is already accepted!")
                return

            elif row[0] is False and row[1] is True:
                await ctx.send(f":x: **ERROR:** {ctx.author.mention}, that bot is denied.")
                return

            elif row[0] is False and row[1] is False:
                await ctx.send(f":x: **ERROR:** {ctx.author.mention}, that bot is on review. When it's accepted or denied, you'll receive a DM.")
                return

            else:
                return

        # If it doesn't exist, create a row on the user_bots table with the bot
        # info.
        self.bot.database_cursor.execute(
            """INSERT INTO user_bots (owner_id, bot_id, description, accepted, reviewed)
            VALUES
            (%s, %s, %s, %s, %s)""",
            (ctx.author.id,
             valid_bot_id,
             textwrap.shorten(
                 description,
                 1710,
                 placeholder="..."),
                False,
                False))

        self.bot.database_connection.commit()

        embed: discord.Embed = discord.Embed(
            title="Bot submit",
            color=self.bot.constants["style"]["colors"]["bot_submission_color"]
        )
        embed.add_field(name="Submittor", value=str(ctx.author), inline=False)
        embed.add_field(
            name="Submittor ID",
            value=str(
                ctx.author.id),
            inline=False)
        embed.add_field(
            name="Invite link",
            value=f"https://discord.com/api/oauth2/authorize?client_id={valid_bot_id}&permissions=104188992&scope=bot",
            inline=False)
        embed.add_field(
            name="Bot description",
            value=description,
            inline=False)
        await bot_submits_mod_channel.send(embed=embed)

        embed: discord.Embed = discord.Embed(
            title="Bot submitted successfully!",
            description=f"Bot submitted succesfully, {ctx.author.mention}! We will DM you if it's approved or denied!",
            color=self.bot.constants["style"]["colors"]["bot_submission_color"])
        await ctx.send(embed=embed)

    @submit.error
    async def submit_error(self, ctx: commands.Context, error: t.Union[Exception, commands.errors.CommandOnCooldown]) -> None:
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.message.delete()
            discord.Message = await ctx.send(f":x: **ERROR:** {ctx.author.mention}, the bot ID or the bot description is missing.")

        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="approve")
    @commands.has_role("Staff")
    async def approve(self, ctx: commands.Context, bot: discord.Member, *, reason: t.Optional[str] = None) -> None:
        """Command to accept user bots."""

        if not reason:
            reason = "No reason specified."

        # Check if the user bot is registered.
        self.bot.database_cursor.execute(
            "SELECT * FROM user_bots WHERE bot_id = %s",
            (bot.id,)
        )

        row = self.bot.database_cursor.fetchone()
        self.bot.database_connection.commit()

        if not row:
            await ctx.send(":x: **ERROR:** That user bot is not submitted.")
            return

        # Check if the user bot was already accepted.
        if row[3] is True:
            await ctx.send(":x: **ERROR:** That user bot is already accepted.")
            return

        self.bot.database_cursor.execute(
            "UPDATE user_bots SET accepted = True, reviewed = True WHERE bot_id = %s",
            (bot.id,)
        )

        self.bot.database_connection.commit()

        # Send a message to the bot owner.
        self.bot.database_cursor.execute(
            "SELECT owner_id FROM user_bots WHERE bot_id = %s",
            (bot.id,)
        )

        row = self.bot.database_cursor.fetchone()
        self.bot.database_connection.commit()

        bot_owner: discord.Member = ctx.guild.get_member(row[0])

        if not bot_owner:
            await ctx.send(f":x: **ERROR:** Could not find the bot owner of {bot.mention}. Kicking the bot and deleting bot submission.")
            self.bot.database_cursor.execute(
                "DELETE FROM user_bots WHERE bot_id = %s",
                (bot.id,)
            )
            self.bot.database_connection.commit()
            await bot.kick(reason="Owner left")

        elif bot_owner:

            try:
                embed: discord.Embed = discord.Embed(
                    title="Accepted!",
                    description=f"Your bot, {bot}, was accepted to our server! Reason:\n\n{textwrap.shorten(reason, 1910, placeholder='...')}",
                    color=self.bot.constants["style"]["colors"]["bot_submission_approved"])
                embed.set_thumbnail(url=bot.avatar_url)
                await bot_owner.send(embed=embed)

            except discord.Forbidden:
                await ctx.send(f":warning: **WARNING:** Could not DM {bot_owner.mention} (the owner of {bot.mention}).")

        # Add the user bot role to the user bot.
        await bot.add_roles(ctx.guild.get_role(self.bot.constants["server"]["bot-roles"]["ids"]["user-bot"]))

        # Remove Bot Testers role.
        await bot.remove_roles(ctx.guild.get_role(self.bot.constants["server"]["bot-roles"]["ids"]["bot-testers"]))

        await ctx.send(f":white_check_mark: **SUCCESS:** {bot.mention} has been approved!")

        # Log it on the mod-log channel (public one).
        mod_log_channel: discord.TextChannel = ctx.guild.get_channel(
            self.bot.constants["server"]["text-channels"]["public"]["mod-logs"])

        if not mod_log_channel:
            await ctx.send(f":warning: **WARNING:** Could not find channel with ID {mod_log_channel}.")

        else:
            embed: discord.Embed = discord.Embed(
                title="Bot approval",
                color=self.bot.constants["style"]["colors"]["bot_submission_approved"])
            embed.add_field(
                name="Submittor",
                value=bot_owner.mention,
                inline=False)
            embed.add_field(
                name="Submittor ID", value=str(
                    bot_owner.id), inline=False)
            embed.add_field(name="Bot", value=bot.mention, inline=False)
            embed.add_field(name="Bot ID", value=bot.id, inline=False)

            await mod_log_channel.send(embed=embed)

    @approve.error
    async def approve_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send(':x: **ERROR:** You don\'t have "Staff" role.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** You missed the bot parameter.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid bot specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="deny")
    @commands.has_role("Staff")
    async def deny(self, ctx: commands.Context, bot: discord.Member, *, reason: str) -> None:
        """Denies a bot submission."""

        # Check if the user bot is registered.
        self.bot.database_cursor.execute(
            "SELECT * FROM user_bots WHERE bot_id = %s",
            (bot.id,)
        )

        row = self.bot.database_cursor.fetchone()
        self.bot.database_connection.commit()

        if not row:
            await ctx.send(":x: **ERROR:** That user bot is not submitted.")
            return

        # Check if the user bot was already accepted.
        if row[3] is False:
            await ctx.send(":x: **ERROR:** That user bot is already denied.")
            return

        self.bot.database_cursor.execute(
            "UPDATE user_bots SET accepted = False, reviewed = True WHERE bot_id = %s",
            (bot.id,)
        )

        self.bot.database_connection.commit()

        # Send a message to the bot owner.
        self.bot.database_cursor.execute(
            "SELECT owner_id FROM user_bots WHERE bot_id = %s",
            (bot.id,)
        )

        row = self.bot.database_cursor.fetchone()
        self.bot.database_connection.commit()

        bot_owner: discord.Member = ctx.guild.get_member(row[0])

        if not bot_owner:
            await ctx.send(f":warning: **WARNING:** Could not find the bot owner of {bot.mention}. Kicking the bot, denying and deleting submission.")
            self.bot.database_cursor.execute(
                "DELETE FROM user_bots WHERE bot_id = %s",
                (bot.id,)
            )
            await bot.kick(reason="Owner left")

        elif bot_owner:
            try:
                embed: discord.Embed = discord.Embed(
                    title="Denied",
                    description=f"Your bot, {bot}, was denied. Reason:\n\n{textwrap.shorten(reason, 1820, placeholder='...')}",
                    color=self.bot.constants["style"]["colors"]["bot_submission_denied"])
                embed.set_thumbnail(url=bot.avatar_url)
                embed.set_footer(
                    text="Contact the staff again if you want us to review the bot again.")
                await bot_owner.send(embed=embed)

            except discord.Forbidden:
                await ctx.send(f":warning: **WARNING:** Could not DM {bot_owner.mention} (the owner of {bot.mention}).")

        await ctx.send(f":white_check_mark: **SUCCESS:** {bot.mention} has been denied.")

        # Log it on the mod-log channel (public one).
        mod_log_channel: discord.TextChannel = ctx.guild.get_channel(
            self.bot.constants["server"]["text-channels"]["public"]["mod-logs"])

        if not mod_log_channel:
            await ctx.send(f":warning: **WARNING:** Could not find channel with ID {mod_log_channel}.")

        else:
            embed: discord.Embed = discord.Embed(
                title="Bot denial",
                color=self.bot.constants["style"]["colors"]["bot_submission_denied"])
            embed.add_field(
                name="Submittor",
                value=bot_owner.mention,
                inline=False)
            embed.add_field(
                name="Submittor ID", value=str(
                    bot_owner.id), inline=False)
            embed.add_field(name="Bot", value=bot.mention, inline=False)
            embed.add_field(name="Bot ID", value=bot.id, inline=False)

            await mod_log_channel.send(embed=embed)

    @deny.error
    async def deny_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send(':x: **ERROR:** You don\'t have "Staff" role.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** You missed the bot parameter or the reason parameter.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid bot specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")

    @commands.command(name="userbot")
    @commands.has_role("Staff")
    async def user_bot(self, ctx: commands.Context, bot: t.Union[int, discord.Member]) -> None:
        """Shows information about a user bot."""

        self.bot.database_cursor.execute(
            "SELECT * FROM user_bots where bot_id = %s",
            (bot if isinstance(bot, int) else bot.id,)
        )

        row = self.bot.database_cursor.fetchone()
        self.bot.database_connection.commit()

        if not row:
            await ctx.send(":x: **ERROR:** That bot is not registered on the database.")
            return

        embed: discord.Embed = discord.Embed(
            title=f"User bot #{row[5]}",
            color=self.bot.constants["style"]["colors"]["normal"]
        )
        embed.add_field(
            name="User bot owner",
            value=f"<@{row[0]}>",
            inline=False)
        embed.add_field(
            name="User bot owner ID",
            value=str(
                row[0]),
            inline=False)
        embed.add_field(
            name="User bot name",
            value=f"<@{row[1]}>",
            inline=False)
        embed.add_field(name="User bot ID", value=str(row[1]), inline=False)
        embed.add_field(name="Description", value=row[2], inline=False)
        embed.add_field(
            name="Invite link",
            value=f"https://discord.com/api/oauth2/authorize?client_id={row[1]}&permissions=104188992&scope=bot",
            inline=False)
        embed.add_field(
            name="Reviewed",
            value="Yes" if row[4] else "No",
            inline=False)
        embed.add_field(
            name="Accepted",
            value="Yes" if row[3] else "No",
            inline=False)
        await ctx.send(embed=embed)

        # https://vine.co/v/eFVeetKwMM7

    @user_bot.error
    async def user_bot_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send(':x: **ERROR:** You don\'t have "Staff" role.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':x: **ERROR:** You missed the bot parameter.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(':x: **ERROR:** Invalid bot specified.')
        else:
            await ctx.send(f":x: **FATAL ERROR:** {error}\nPlease, contact the moderation team as soon as possible.")


def setup(bot: Bot) -> None:
    bot.add_cog(UserbotsCog(bot))
