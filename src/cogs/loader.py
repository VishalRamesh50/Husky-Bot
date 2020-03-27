from discord.ext import commands

from main import COGS_DIRECTORY
from checks import is_admin


class Loader(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.COGS_DIRECTORY = "cogs"

    @is_admin()
    @commands.command()
    async def load(self, ctx: commands.Context, extension: str) -> None:
        """Loads the given extension.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        extension: `str`
            The extension/cog to load.
        """
        try:
            self.client.load_extension(f"{COGS_DIRECTORY}.{extension}")
            await ctx.send(f"{extension} has been loaded.")
        except Exception as e:
            await ctx.send(f"{extension} was unable to be loaded. [{e}]")

    @is_admin()
    @commands.command()
    async def unload(self, ctx: commands.Context, extension: str) -> None:
        """Unloads the given extension.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        extension: `str`
            The extension/cog to unload.
        """
        try:
            self.client.unload_extension(f"{COGS_DIRECTORY}.{extension}")
            await ctx.send(f"{extension} has been unloaded.")
        except Exception as e:
            await ctx.send(f"{extension} was unable to be unloaded. [{e}]")


def setup(client: commands.Bot):
    client.add_cog(Loader(client))
