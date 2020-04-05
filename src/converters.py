import discord
from discord.ext import commands
from discord.ext.commands import RoleConverter, BadArgument
from typing import Optional


class CourseRoleConverter(RoleConverter):
    """Converts to a `discord.Role` with some leeway for courses.

    All lookups are via the local guild. If in a DM context, then the lookup
    is done by the global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name
    4. Lookup by name (case-insensitive and ignoring dashes)
    """

    def __ignore_dash_case(self, argument: str) -> str:
        """Returns a lower-case string without dashes and stripping whitespace."""
        return " ".join(argument.split("-")).lower().strip()

    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> Optional[discord.Role]:
        result: Optional[discord.Role] = None
        guild: discord.Role = ctx.guild
        try:
            result = await super().convert(ctx, argument)
            if result:
                return result
        except BadArgument:
            pass
        for r in guild.roles:
            if self.__ignore_dash_case(argument) == self.__ignore_dash_case(r.name):
                result = r
                break

        if result is None:
            raise BadArgument(f'Role "{argument}" not found.')
        return result
