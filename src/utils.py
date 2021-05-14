import discord
from typing import Optional, Tuple

from client.bot import Bot, ChannelType


def required_configs(*channel_types: Tuple[ChannelType]):
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

    Remember: If adding this to an event. It must come before (below) the @listener decorator.
    """

    def decorator(function):
        async def wrapper(*args, **kwargs):
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

        wrapper.__name__ = function.__name__
        return wrapper

    return decorator
