import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions
from typing import Callable, Optional

from errors import InvalidChannel

"""A group of decorators which can be used as Discord checks on any command."""


def in_channel(channel_id: int) -> Callable:
    """Checks if the message sent was from the given channel id.

    Parameters
    ----------
    channel_id: `int`
        The channel id matching the channel that the message sent must be in.

    Raises
    ----------
    InvalidChannel if the message was not sent in the correct channel.
    """

    def predicate(ctx: commands.Context) -> bool:
        """Determines if the message was sent in the correct channel.
        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.

        Returns
        ----------
        True if the message sent was in the channel.

        Raises
        ----------
        InvalidChannel if the message was not sent in the correct channel.
        """

        guild: Optional[discord.Guild] = ctx.guild
        if guild is None:
            raise InvalidChannel
        in_channel: bool = ctx.channel.id == channel_id
        if not in_channel:
            channel: discord.TextChannel = discord.utils.get(
                guild.channels, id=channel_id
            )
            if channel:
                raise InvalidChannel(channel.mention)
            else:
                raise InvalidChannel
        return True

    return commands.check(predicate)


def is_admin() -> Callable:
    """Checks if the author who sent the message has admin permissions.

    Raises
    ----------
    MissingPermissions if the user does not have admin permissions.
    """

    return commands.has_permissions(administrator=True)


def is_mod() -> Callable:
    """Checks if the author who sent the message was a moderator.

    Raises
    ----------
    MissingPermissions if the author is not a moderator.
    """

    def predicate(ctx: commands.Context) -> bool:
        """Determines if the author is a moderator.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.

        Returns
        ----------
        True if the author of the message is a Moderator.

        Raises
        ----------
        MissingPermissions if the author is not a Moderator.
        """
        mod: Optional[discord.Role] = discord.utils.get(
            ctx.author.roles, name="Moderator"
        )
        if mod is None:
            raise MissingPermissions(["Moderator"])

        return True

    return commands.check(predicate)
