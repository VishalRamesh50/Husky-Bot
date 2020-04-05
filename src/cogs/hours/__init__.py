from discord.ext import commands

from .hours import Hours


def setup(client: commands.Bot):
    client.add_cog(Hours(client))
