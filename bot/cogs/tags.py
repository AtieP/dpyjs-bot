"""Tag management."""

import os
import typing as t

from bot.bot import Bot
from discord.ext import commands
from difflib import SequenceMatcher

class TagCog(commands.Cog):
    """Tag management cog class."""

    def __init__(self, bot: Bot) -> None:
        """Takes a parameter that must be an instance of bot.bot.Bot (see /bot/bot.py)."""

        self.bot = bot
        self.__load_tags()

    def __load_tags(self) -> None:
        """Loads a dict with all cogs located on /bot/resources/tags."""

        self.bot.logger_info("Loading tags...")

        self.tags_dict: t.Dict[str, str] = {}

        for file in os.listdir("bot/resources/tags"):

            self.bot.logger_info(f"Loading tag {os.path.splitext(file)[0]}...")

            if not file.endswith(".md"):
                return

            with open(f"bot/resources/tags/{file}") as target_file:
                file_content = target_file.read()

            # filename with no extension = file content
            self.tags_dict[os.path.splitext(file)[0]] = file_content

            self.bot.logger_info(f"Finished loading tag {os.path.splitext(file)[0]}")

        self.bot.logger_info("Finished loading tags")

    @commands.command(name="tag")
    async def tag(self, ctx: commands.Context, tag_name: str) -> None:
        """Sends a specific tag."""

        try:
            embed: discord.Embed = discord.Embed(description=self.tags_dict[tag_name], color=self.bot.constants["style"]["colors"]["normal"])
            await ctx.send(embed=embed)

        except KeyError:
            # Return tags with similar name.
            similar_tags = ""
            found_similar_tag = False

            for tag in self.tags_dict.keys():
                if TagCog.similar(tag_name, tag) > 0.6:
                    found_similar_tag = True
                    similar_tags += f"`{tag}` "

            if found_similar_tag:
                await ctx.send(f"Could not find that tag. Did you mean one of these?\n{similar_tags}")
            else:
                await ctx.send(f"Could not find that tag.")

    @commands.command(name="tags")
    async def tags(self, ctx: commands.Context) -> None:
        """Sends an embed with all the tags available."""

        tags: str = f"To display a tag, run {self.bot.constants['bot']['prefix']}<tag name>.\n\n"
        for tag in self.tags_dict.keys():
            tags += f"`{tag}` "

        embed: discord.Embed = discord.Embed(title="Available tags", description=tags, color=self.bot.constants["style"]["colors"]["normal"])
        await ctx.send(embed=embed)

    @staticmethod
    def similar(a, b) -> bool:
        return SequenceMatcher(None, a, b).ratio()


def setup(bot: Bot) -> None:
    bot.add_cog(TagCog(bot))
