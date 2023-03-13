from discord.ext import commands

from .reaction_role import ReactionRole
from .reaction_channel import ReactionChannel


async def setup(client: commands.Bot):
    await client.add_cog(ReactionRole(client))
    await client.add_cog(ReactionChannel(client))
