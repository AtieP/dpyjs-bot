import logging
from datetime import datetime

from bot.bot import Bot
from bot.constants import Colors, Roles

from discord import AllowedMentions, Color, Embed
from discord.ext import commands


logger = logging.getLogger(__name__)


class TagsCog(commands.Cog):
    """Has commands related to tags."""

    def __init__(self, bot: Bot) -> None:
        """Definiting a bot variable."""
        self.bot = bot

    async def get_tag(self, name: str):
        """Fetch a tag and its values."""
        tag = await self.bot.database_connection.fetchrow(
            "SELECT * FROM tags WHERE name = $1", name, timeout=5
        )
        return tag

    async def list_tag(self):
        """Fetch a tag and its values."""
        tag = await self.bot.database_connection.fetch(
            "SELECT * FROM tags", timeout=5
        )
        return tag

    async def add_tag(self, name: str, content: str,
                      owner_id: int, created_at: datetime) -> None:
        """Add new tag to database."""
        await self.bot.database_connection.execute(
            """INSERT INTO tags(
                name, content,
                owner_id, created_at
            ) VALUES ($1, $2, $3, $4)""",
            name, content, owner_id, created_at
        )

    async def remove_tag(self, name: str) -> None:
        """Remove a tag from database."""
        await self.bot.database_connection.execute(
            "DELETE FROM tags WHERE name = $1", name
        )

    async def edit_tag(self, type: int, name: str, content: str):
        """Edit a tag."""
        # 0 = update name
        if type == 0:
            await self.bot.database_connection.execute(
                "UPDATE tags SET name = $1 WHERE name = $2",
                content, name
            )
        # 1 = update content
        else:
            await self.bot.database_connection.execute(
                "UPDATE tags SET content = $1 WHERE name = $2",
                content, name
            )

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: commands.Context, *, tag_name: str) -> None:
        """Returns the content of a tag."""
        content = await self.get_tag(tag_name)
        if not content:
            return await ctx.send("That tag is not found.")
        content = dict(content)
        await ctx.send(content["content"],
                       allowed_mentions=AllowedMentions(everyone=False))

    @tag.command(aliases=["create"])
    @commands.has_role(Roles.staff)
    async def add(self, ctx: commands.Context, name: str, *, content: str):
        """Add new tag."""
        subcommands_protected = [
            "add", "remove", "rem", "edit", "create",
            "del", "delete", "rm", "list", "info"
        ]
        if await self.get_tag(name) or name in subcommands_protected:
            return await ctx.send("I can't create the tag with that name "
                                  + "because it's in subcommands of `tag`"
                                  + " command or already taken from "
                                  + "database\n"
                                  + f"You may try again like this `{name}1`"
                                  + f"or this `new_{name}`")
        else:
            await self.add_tag(name, content,
                               ctx.author.id, ctx.message.created_at)
            return await ctx.send(f"Your new tag **{name}** has been added!")

    @tag.command(aliases=["rm", "del", "delete", "rem"])
    @commands.has_role(Roles.staff)
    async def remove(self, ctx: commands.Context, name: str):
        """Remove a tag from database."""
        if not await self.get_tag(name):
            return await ctx.send(f"The tag **{name}** is already removed")
        await self.remove_tag(name)
        await ctx.send(f"The tag **{name}** has been removed!")

    @tag.group()
    @commands.has_role(Roles.staff)
    async def edit(self, ctx: commands.Context):
        """Edit the tag's name or content."""
        if not ctx.invoked_subcommand:
            return await ctx.send(
                "You need to use subcommands below:\n"
                + "`content`, `name`"
            )

    @edit.command()
    async def content(self, ctx: commands.Context, name: str, *, text: str):
        """Edit a content of a tag."""
        if not await self.get_tag(name):
            return await ctx.send("That tag is not found.")
        await self.edit_tag(1, name, text)
        await ctx.send("Successfully edited new content of a tag!")

    @edit.command()
    async def name(self, ctx: commands.Context, name: str, *, text: str):
        """Edit a name of a tag."""
        if not await self.get_tag(name):
            return await ctx.send("That tag is not found.")
        await self.edit_tag(0, name, text)
        await ctx.send("Successfully edited new name of a tag!")

    @tag.command(name="list")
    async def _list(self, ctx: commands.Context) -> None:
        """View list of tags stored in database."""
        lists = await self.list_tag()
        lists = map(lambda x: f"**{x['name']}**", lists)
        embed = Embed(title="List tags", color=Colors.orange)
        embed.description = ", ".join(lists)
        await ctx.send(embed=embed)

    @tag.command()
    async def info(self, ctx: commands.Context, name: str):
        """View information about a specific tag by name."""
        tag = await self.get_tag(name)
        if not tag:
            return await ctx.send("That tag is not found")
        user = await self.bot.fetch_user(tag['owner_id'])
        embed = Embed(title=f"Tag info - {tag['name']}", color=Color.gold())
        embed.set_thumbnail(url=str(user.avatar_url))
        embed.timestamp = tag['created_at']
        embed.set_footer(
            text="Created at", icon_url=str(ctx.author.avatar_url)
        )
        embed.description = f"""**Name:** {tag['name']}
        **Who created:** {user.name} ({tag['owner_id']})
        **Created at:** {tag['created_at'].strftime("%d/%m/%Y, %H:%M:%S")}"""
        return await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(TagsCog(bot))
