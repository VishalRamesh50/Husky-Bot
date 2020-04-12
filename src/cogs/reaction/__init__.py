from discord.ext import commands

from .reaction_role import ReactionRole


def setup(client: commands.Bot):
    client.add_cog(ReactionRole(client))
