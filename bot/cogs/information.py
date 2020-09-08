import textwrap

from bot.bot import Bot
from bot.constants import Colors, Emojis, Roles
from bot.utils.checks import with_role

from discord import Embed, Member, Role, Status, TextChannel
from discord.ext import commands


class InformationCog(commands.Cog):
    """Has commands related to member and server information."""

    @commands.command(name="user", aliases=("member",))
    async def user(self, ctx: commands.Context, member: Member = None) -> None:
        """Shows information about a member of our community."""
        if member is None:
            member = ctx.author
        elif member != ctx.author and not with_role(ctx, Roles.staff):
            await ctx.send(
                ":x: **ERROR:** Sorry, but you can use this command "
                "only on yourself."
            )
            return

        member_roles = " ".join(
            role.mention for role in member.roles if role.name != "@everyone"
        )

        member_information = Embed(
            title=member.nick if member.nick else str(member),
            color=member.top_role.color
        )
        member_information.add_field(
            name="User information",
            value=textwrap.dedent(f"""
                Created at: {member.created_at}
                User ID: {member.id}
            """),
            inline=False
        )
        member_information.add_field(
            name="Member information",
            value=textwrap.dedent(f"""
                Joined at: {member.joined_at}
                Roles: {member_roles}
            """),
            inline=False
        )
        member_information.set_thumbnail(
            url=member.avatar_url_as(static_format="png")
        )
        await ctx.send(embed=member_information)

    @commands.command(name="server")
    async def server(self, ctx: commands.Context) -> None:
        """Shows information about the server."""
        statuses_emojis = {
            "online": Emojis.status_online,
            "idle": Emojis.status_idle,
            "dnd": Emojis.status_dnd,
            "offline": Emojis.status_offline
        }

        online_members = 0
        idle_members = 0
        dnd_members = 0
        offline_members = 0

        for member in ctx.guild.members:
            if member.status is Status.online:
                online_members += 1
            elif member.status is Status.idle:
                idle_members += 1
            elif member.status is Status.dnd:
                dnd_members += 1
            elif member.status is Status.offline:
                offline_members += 1
        staff_members = len(
            ctx.guild.get_role(Roles.staff).members
        )
        trial_staff_members = len(
            ctx.guild.get_role(Roles.trial_staff).members
        )

        server_information = Embed(
            title=f"{ctx.guild.name}",
            color=Colors.default
        )
        server_information.add_field(
            name="General information",
            value=textwrap.dedent(f"""
                Created at: {ctx.guild.created_at}
                Region: {ctx.guild.region}
                Features: {', '.join(ctx.guild.features)}
            """),
            inline=False
        )
        server_information.add_field(
            name="Channels",
            value=textwrap.dedent(f"""
                Text channels: {len(ctx.guild.text_channels)}
                Voice channels: {len(ctx.guild.voice_channels)}
            """),
            inline=False
        )
        server_information.add_field(
            name="Members count",
            value=textwrap.dedent(f"""
                Members: {len(ctx.guild.members)}
                Staff members: {staff_members}
                Trial staff members: {trial_staff_members}
            """),
            inline=False
        )
        server_information.add_field(
            name="Member statuses",
            value=textwrap.dedent(f"""
                {statuses_emojis['online']} {online_members}
                {statuses_emojis['idle']} {idle_members}
                {statuses_emojis['dnd']} {dnd_members}
                {statuses_emojis['offline']} {offline_members}
            """),
            inline=False
        )
        server_information.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=server_information)

    @commands.command(name="role")
    @commands.has_role(Roles.staff)
    async def role(self, ctx: commands.Context, role: Role) -> None:
        """Shows information about a role."""
        role_information = Embed(
            color=role.color
        )
        role_information.add_field(
            name=f'General information about "{role.name}" role',
            value=textwrap.dedent(f"""
                ID: {role.id}
                Members with role: {len(role.members)}
                Created at: {role.created_at}
                Hex color: {role.color}
                Position: {role.position}
            """),
            inline=False
        )
        role_information.add_field(
            name="Permissions",
            value=", ".join(
                name for name, value in role.permissions if value
            ),
            inline=False
        )
        await ctx.send(embed=role_information)

    @commands.command(name="channel")
    @commands.has_role(Roles.staff)
    async def channel(
        self,
        ctx: commands.Context,
        channel: TextChannel
    ) -> None:
        """Shows information about a channel."""
        channel_information = Embed(
            color=Colors.default
        )
        channel_information.add_field(
            name=f"General information about #{channel} channel",
            value=textwrap.dedent(f"""
                Name: {channel.name}
                ID: {channel.id}
                Created at: {channel.created_at}
                Slowmode: {channel.slowmode_delay} seconds
            """),
            inline=False
        )
        await ctx.send(embed=channel_information)


def setup(bot: Bot) -> None:
    """Loads the cog into the bot."""
    bot.add_cog(InformationCog())
