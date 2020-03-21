import discord
from discord.ext import commands


"""A group of decorators which can be used as Discord checks on any command."""


def in_channel(channel_id: int) -> bool:
    """Checks if the message sent was from the given channel id.

    Parameters
    ----------
    channel_id: `int`
        The channel id matching the channel that the message sent must be in.

    Returns
    ----------
    True if the message sent was in the channel
    with the given channel id else False.
    """

    def predicate(ctx: commands.Context):
        in_channel: bool = ctx.channel.id == channel_id
        if not in_channel:
            ctx.bot.failed_command_channel_map[ctx.command.name] = channel_id
        return in_channel

    return commands.check(predicate)


def is_admin() -> bool:
    """Checks if the author who sent the message has admin permissions.

    Returns
    ----------
    True if the author of the sent message
    has admin permission in the guild else False.
    """

    def predicate(ctx: commands.Context):
        return ctx.author.permissions_in(ctx.channel).administrator

    return commands.check(predicate)


def is_mod() -> bool:
    """Checks if the author who sent the message was a moderator.

    Returns
    ----------
    True if the author of the sent message has
    the Role: 'Moderator' else False.
    """

    def predicate(ctx: commands.Context):
        return discord.utils.get(ctx.author.roles, name="Moderator") is not None

    return commands.check(predicate)
