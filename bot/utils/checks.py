from discord.abc import Snowflake
from discord.ext import commands


def with_role(ctx: commands.Context, *role_ids: Snowflake) -> bool:
    """
    Returns True if the user has any of the roles in role_ids.

    Otherwise, it returns False.
    """
    if not ctx.guild:
        return False

    for role in ctx.author.roles:
        if role.id in role_ids:
            return True
    else:
        return False
