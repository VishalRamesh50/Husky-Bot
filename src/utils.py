import discord
import functools
from datetime import datetime
from discord.ext import commands
from math import ceil, floor
from pytz import timezone
from typing import List, Optional, Tuple

from client.bot import Bot, ChannelType


def required_configs(*channel_types: ChannelType):
    """A decorator which checks that the method should be run by checking if the guild
    has configured the required channels for this function to be executed.

    Different Cases
    ----------------
    - Guild could not be found from the arguments. (Fail)
    - Guild could be found from an argument but it is None. (Fail)
    - Guild could be found form an argument and it is a valid guild.
        - One/None of the requested channel types are configured for the guild. (Fail)
        - All the requested channel types are configured for the guild. (Pass)

    Based on the above cases, if something is considered a "Fail", the function it
    decorates will never be called and will be skipped. If it is considered to be a "Pass",
    then the function will be called as normal.

    Remember: When adding this to a function make sure it's the first decorator added.
    It must come before (below) the @listener or @commands decorator.
    """

    def decorator(function):
        @functools.wraps(function)
        async def wrapper(*args, **kwargs) -> None:
            client: Bot = args[0].client
            for arg in args[1:]:
                # Try to get `.guild_id` directly
                guild_id: Optional[int] = getattr(arg, "guild_id", None)
                # Try to get `.guild` directly, otherwise try to get `.message.guild`, otherwise give up
                guild: Optional[discord.Guild] = getattr(
                    arg, "guild", getattr(getattr(arg, "message", None), "guild", None)
                )
                if guild:
                    guild_id = guild.id
                if guild_id:
                    for channel_type in channel_types:
                        if not client._get_channel(guild_id, channel_type):
                            return
                else:
                    return
                break
            else:
                return
            result = await function(*args, **kwargs)
            return result

        return wrapper

    return decorator


class PaginatedEmbed:
    emoji_number_map = {"1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5, "6️⃣": 6}
    prev_page_emoji = "⏪"
    next_page_emoji = "⏩"
    cancel_emoji = "❌"
    valid_emojis = set(emoji_number_map.keys()).union(
        {prev_page_emoji, next_page_emoji, cancel_emoji}
    )

    def __init__(
        self,
        title: str,
        description: str,
        options: List[Tuple[str, str]],
        per_page: int = 6,
    ) -> None:
        self.options: List[Tuple[str, str]] = options
        self.total_num_options: int = len(options)
        self.per_page: int = per_page
        self.max_num_pages: int = ceil(self.total_num_options / self.per_page)
        self.current_page: int = 1
        self.embed = discord.Embed(title=title, description=description)

    @property
    def has_prev(self) -> bool:
        return self.current_page > 1

    @property
    def has_next(self) -> bool:
        return self.current_page < self.max_num_pages

    async def _change_page(self, page_num: int, message: discord.Message):
        if not (1 <= page_num <= self.max_num_pages):
            return

        starting_option_index: int = (page_num - 1) * self.per_page
        ending_option_index: int = starting_option_index + self.per_page
        self.embed.clear_fields()
        for index, option in enumerate(
            self.options[starting_option_index:ending_option_index]
        ):
            name, value = option
            option_num: int = index + 1
            self.embed.add_field(name=f"{option_num}. {name}", value=value)

        self.embed.set_footer(text=f"Page {page_num}/{self.max_num_pages}")
        await message.edit(embed=self.embed)
        self.current_page = page_num

    async def _next_page(self, message: discord.Message):
        await self._change_page(self.current_page + 1, message)

    async def _previous_page(self, message: discord.Message):
        await self._change_page(self.current_page - 1, message)

    async def send(
        self, ctx: commands.Context, author: discord.User, client: discord.Client
    ) -> Optional[int]:
        """
        Returns
        ----------
        Option index if one is selected, else None if cancelled.

        Raises
        ----------
        asyncio.TimeoutError If the reaction timeout expires.
        """
        message: discord.Message = await ctx.send(embed=self.embed)

        await self._change_page(1, message)
        await message.add_reaction(PaginatedEmbed.prev_page_emoji)
        await message.add_reaction(PaginatedEmbed.next_page_emoji)
        for emoji in PaginatedEmbed.emoji_number_map:
            await message.add_reaction(emoji)
        await message.add_reaction(PaginatedEmbed.cancel_emoji)

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                user == author
                and reaction.message.id == message.id
                and str(reaction) in PaginatedEmbed.valid_emojis
            )

        while True:
            reaction, _ = await client.wait_for(
                "reaction_add", timeout=60.0, check=check
            )
            emoji: str = reaction.emoji
            if emoji == PaginatedEmbed.prev_page_emoji:
                await self._previous_page(message)
            elif emoji == PaginatedEmbed.next_page_emoji:
                await self._next_page(message)
            elif emoji == PaginatedEmbed.cancel_emoji:
                return None
            else:
                selected_num: int = PaginatedEmbed.emoji_number_map[emoji]
                return self.per_page * (self.current_page - 1) + (selected_num - 1)


def timestamp_format(date: datetime) -> str:
    """Takes a datetime and then formats it as a Discord timestamp formatted string.

    Parameters
    ------------
    date: `datetime`
        A timezone aware or naive datetime. If naive it is assumed to be UTC.

    Returns
    ---------
    A string in the format: "Month DD, YYYY H:MM:SS AM/PM" when rendered
    """
    if date.tzinfo is None:
        date = timezone("UTC").localize(date)
    epoch: int = floor(date.timestamp())
    return f"<t:{epoch}:D> <t:{epoch}:T>"


def member_mentioned_roles(member: discord.Member) -> str:
    """Creates a string of mentioned roles of the member with spaces to separate
    them in order of highest to lowest excluding the @everyone role.

    Parameters
    ------------
    member: `discord.Member`
        The member used to get the roles of.

    Returns
    ---------
    A string in the format: "@Role1 @Role2" if there is at least one role other than @everyone.
    Otherwise, returns "NO ROLES"
    """
    roles: str = ""
    for role in reversed(member.roles[1:]):
        roles += role.mention + " "
    roles = "NO ROLES" if roles == "" else roles
    return roles


def member_join_position(member: discord.Member) -> int:
    """Computes the join position of a member in a guild.
    Aka out of X members what number did this member join at.

    Parameters
    ------------
    member: `discord.Member`
        The member to compute the join position of.

    Returns
    ---------
    A integer representing the join position of the member for their guild.
    """
    return (
        sorted(member.guild.members, key=lambda m: m.joined_at or datetime.max).index(
            member
        )
        + 1
    )
