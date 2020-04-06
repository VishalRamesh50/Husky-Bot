import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, MemberConverter, RoleConverter
from typing import List


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

    async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
        try:
            return await super().convert(ctx, argument)
        except BadArgument:
            pass
        for r in ctx.guild.roles:
            if self.__ignore_dash_case(argument) == self.__ignore_dash_case(r.name):
                return r

        raise BadArgument(f'Role "{argument}" not found.')


class FuzzyMemberConverter(MemberConverter):
    """Converts to a `discord.Member`

    All lookups are via the local guild. If in a DM context, then the lookup
    is done by the global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name#discrim
    4. Lookup by name
    5. Lookup by nickname
    6. Lookup by name/nickname (case-insensitive)
    8. Fuzzy lookup by name/nickname (case-insensitive).
        Resolves if the argument is in those names. Doesn't need to be exact match.
    """

    async def convert(self, ctx: commands.Context, argument: str) -> discord.Member:
        try:
            return await super().convert(ctx, argument)
        except BadArgument:
            pass
        argument = argument.lower()
        members: List[discord.Member] = ctx.guild.members
        for m in members:
            if argument == m.display_name.lower() or argument == m.name.lower():
                return m
        for m in members:
            if argument in m.display_name.lower() or argument in m.name.lower():
                return m

        raise BadArgument(f'Member "{argument}" not found')
