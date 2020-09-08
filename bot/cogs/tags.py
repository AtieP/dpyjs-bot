import logging
import os

from bot.bot import Bot
from bot.constants import Colors

from discord import Embed
from discord.ext import commands


logger = logging.getLogger(__name__)


class TagsCog(commands.Cog):
    """Has commands related to tags."""

    def __init__(self) -> None:
        """Sets up the cog."""
        self.all_tags = {}

        for tag in os.listdir("bot/resources/tags/"):
            if not tag.endswith(".md"):
                continue

            with open(f"bot/resources/tags/{tag}", "r") as tag_file:
                self.all_tags[tag.rstrip(".md")] = tag_file.read()

            logger.info(f"Tag {tag.rstrip('.md')} loaded")

    @commands.command(name="tag")
    async def tag(self, ctx: commands.Context, tag_name: str) -> None:
        """Returns the content of a tag in an embed."""
        try:
            tag_content = self.all_tags[tag_name]
        except KeyError:
            raise commands.errors.BadArgument(f"Tag {tag_name} not found.")

        tag_embed = Embed(
            title=tag_name,
            description=tag_content,
            color=Colors.default
        )
        await ctx.send(embed=tag_embed)

    @commands.command(name="tags")
    async def tags(self, ctx: commands.Context) -> None:
        """Returns all available tags on an embed."""
        tags_ = Embed(
            title="All available tags",
            description=", ".join(tag for tag in self.all_tags),
            color=Colors.default
        )
        await ctx.send(embed=tags_)


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(TagsCog())
