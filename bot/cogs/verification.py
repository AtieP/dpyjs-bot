"""Verification cog."""

import discord
import discord.utils
import textwrap

from discord.ext import commands
from captcha.image import ImageCaptcha
from bot.bot import Bot
from random import randint
from asyncio.exceptions import TimeoutError


class VerificationCog(commands.Cog):
    """The verification cog class."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Listener that is triggered every time a member joins the server.

        This sends a captcha to the specified user, and if completed, give him the
        default role."""

        # Text and description of the embed.
        embed = discord.Embed(title="Welcome!", description=textwrap.dedent("""Welcome to Discord.py and Discord.js Discord server!

        We are a community that aims to help both beginners and professionals
        who are into Discord.py and/or Discord.js. We also have code examples,
        and you can invite your bot to our server!

        **To verify, please type the content of the following captcha.
        You have 20 seconds to type it.**"""),
        color=self.bot.constants["style"]["colors"]["normal"])

        await member.send(embed=embed)
        await self.__verify(member)

    @commands.command(name="verify")
    async def verify(self, ctx: commands.Context) -> None:
        """Command to verify in case the user failed the verification.

        This musn't be triggered on DMs."""

        if ctx.channel.name != self.bot.constants["server"]["text-channels"]["public"]["verify"]:
            return

        if not ctx.guild:
            return

        msg = ctx.message
        await msg.delete()

        await self.__verify(ctx.author)

    async def __verify(self, member: discord.Member) -> None:
        """The core of the verification.

        This sends an image to the user, and if he types correctly the content
        of the image, it gives to him the default role that grants access to the server."""

        # Create the random number that will be displayed on the captcha.
        number: int = randint(0, 100000)

        # Create the captcha and save it temporarily.
        captcha = ImageCaptcha(fonts=["bot/resources/fonts/captcha/good-times-rg.ttf"])
        captcha.write(str(number), "temp/captcha.png", format="png")

        # The captcha file.
        captcha_file = discord.File("temp/captcha.png", filename="captcha.png")

        # Send image.
        message_sent = await member.send(file=captcha_file)

        def check(m: discord.Message):
            """
            Returns True if the message was typed on the same channel the image
            was sent and it's the image content."""
            return m.channel == message_sent.channel and m.content == str(number)

        try:
            await self.bot.wait_for('message', check=check, timeout=20)

        except TimeoutError:
            await message_sent.channel.send(f"Verification failed because you ran out of time. Run {self.bot.constants['bot']['prefix']}verify on <#{self.bot.constants['server']['text-channels']['public']['verify']}> to try again.")
            return

        # Embed to send to the user when it verified.
        embed = discord.Embed(title="Verification completed!", description=textwrap.dedent(f"""
        Thanks for verifying! Please visit:

        <#{self.bot.constants['server']['text-channels']['public']['rules']}> - Our server rules
        <#{self.bot.constants['server']['text-channels']['public']['announcements']}> - Server announcements
        <#{self.bot.constants['server']['text-channels']['public']['general']}> - On-topic chat
        <#{self.bot.constants['server']['text-channels']['public']['international']}> - International chat
        <#{self.bot.constants['server']['text-channels']['public']['py-development']}> - Python help
        <#{self.bot.constants['server']['text-channels']['public']['js-development']}> - Javascript help
        <#{self.bot.constants['server']['text-channels']['public']['how-to-python']}> - Python examples
        <#{self.bot.constants['server']['text-channels']['public']['how-to-javascript']}> - Javascript examples"""),
        color=self.bot.constants["style"]["colors"]["normal"])

        # Send embed.
        await member.send(embed=embed)

        # This is only executed if the check function returned True and the timeout didn't pass.
        # Add role to user.
        role_to_assign = member.guild.get_role(self.bot.constants["server"]["public-roles"]["ids"]["human"])
        await member.add_roles(role_to_assign, reason="User verified")


def setup(bot: Bot) -> None:
    bot.add_cog(VerificationCog(bot))
