import discord
from discord.ext import commands
from discord.ext.commands import (
    BadArgument,
    Converter,
    MemberConverter,
    NoPrivateMessage,
    RoleConverter,
)
from typing import Optional, Sequence

from regex_patterns import IS_COURSE


class CourseChannelConverter(Converter):
    """Converts to a `discord.TextChannel` if a valid course channel is found.

    All lookups are via the local guild.

    The lookup strategy is as follows (in order):

    1. Lookup by name (case-insensitive, dash-insensitive)
    It looks to see that the name of the argument matches with the description of
    the course channel. Every course channel will have the name of the course in the
    description.
    """

    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> discord.TextChannel:
        guild: discord.Guild = ctx.guild
        if guild is None:
            raise NoPrivateMessage
        # if the role seems to follow a valid course format
        if IS_COURSE.match(argument.upper()) or IS_COURSE.match(
            argument.replace(" ", "-").upper()
        ):
            if "-" in argument:
                course_category, course_num = [w.upper() for w in argument.split("-")]
            else:
                course_category, course_num = [w.upper() for w in argument.split(" ")]
            category: Optional[discord.CategoryChannel] = discord.utils.get(
                guild.categories, name=course_category
            )
            if category is not None:
                for c in category.text_channels:
                    if c.topic and c.topic.startswith(
                        f"{course_category}-{course_num}"
                    ):
                        return c
            raise BadArgument(f'Course "{argument}" not found.')
        raise BadArgument(f'"{argument}" is an invalid course format.')


class CaseInsensitiveRoleConverter(RoleConverter):
    """Converts to a `discord.Role` in a case-insensitive matter.

    All lookups are via the local guild.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name
    4. Lookup by name (case-insensitive)
    """

    def __ignore_case(self, argument: str) -> str:
        """Returns a lower-case string and stripping whitespace."""
        return argument.strip().lower()

    async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
        try:
            return await super().convert(ctx, argument)
        except BadArgument:
            pass
        guild: Optional[discord.Guild] = ctx.guild
        if guild is None:
            raise NoPrivateMessage
        for r in guild.roles:
            if self.__ignore_case(argument) == self.__ignore_case(r.name):
                return r

        raise BadArgument(f'Role "{argument}" not found.')


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
        guild: Optional[discord.Guild] = ctx.guild
        if guild is None:
            raise NoPrivateMessage
        for r in guild.roles:
            if self.__ignore_dash_case(argument) == self.__ignore_dash_case(r.name):
                return r

        raise BadArgument(f'Role "{argument}" not found.')


class FuzzyMemberConverter(MemberConverter):
    """Converts to a `discord.Member`

    All lookups are via the local guild.

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
        guild: Optional[discord.Guild] = ctx.guild
        if guild is None:
            raise NoPrivateMessage
        members: Sequence[discord.Member] = guild.members
        for m in members:
            if argument == m.display_name.lower() or argument == m.name.lower():
                return m
        for m in members:
            if argument in m.display_name.lower() or argument in m.name.lower():
                return m

        raise BadArgument(f'Member "{argument}" not found')
