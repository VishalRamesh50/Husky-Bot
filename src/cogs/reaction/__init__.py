from discord.ext import commands

from .reaction_role import ReactionRole
from .reaction_channel import ReactionChannel


def setup(client: commands.Bot):
    client.add_cog(ReactionRole(client))
    client.add_cog(ReactionChannel(client))
