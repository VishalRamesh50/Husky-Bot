from discord.ext import commands

from .hours import Hours


async def setup(client: commands.Bot):
    await client.add_cog(Hours(client))
