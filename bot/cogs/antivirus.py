import logging
from os.path import splitext

from bot.bot import Bot
from bot.constants import Colors, Roles, WhitelistedFileExtensions

from discord import Embed, Message
from discord.ext import commands

logger = logging.getLogger(__name__)

NOT_ALLOWED_FILE_EXTENSION_MSG = (
    "{}, it seems you tried to attach a file with a type we don't allow ({}). "
    "We only allow these file types: **{}.** If you was trying to attach a "
    "source code file, please, use a pasting service."
)


class AntiMalwareCog(commands.Cog):
    """Has a message listener that checks for malicious file extensions."""

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Checks blacklisted file extensions."""
        if not message.guild or not message.attachments:
            return

        # Check if the user has Administrator role
        for role in message.author.roles:
            if role.id == Roles.admins or role.id == Roles.owner:
                return

        for attachment in message.attachments:
            _, extension = splitext(attachment.url)
            if extension.lower() not in WhitelistedFileExtensions.whitelist:
                break
        else:
            return

        await message.delete()

        logger.info((
            f"{message.author} ({message.author.id}) sent a file with a "
            f"blacklisted extension ({extension})."
        ))

        embed = Embed(
            color=Colors.default,
            description=NOT_ALLOWED_FILE_EXTENSION_MSG.format(
                message.author.mention,
                extension,
                " ".join(WhitelistedFileExtensions.whitelist).rstrip()
            )
        )
        await message.channel.send(embed=embed)


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(AntiMalwareCog())
