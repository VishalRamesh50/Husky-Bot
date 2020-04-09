import discord
import random
from discord.ext import commands
from checks import is_admin, in_channel, is_mod

from data.ids import BOT_SPAM_CHANNEL_ID


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
    async def ping(self, ctx: commands.Context):
        """Sends a message which contains the Discord WebSocket protocol latency.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """

        await ctx.send(f"Pong! {round(self.client.latency * 1000)}ms")

    @is_admin()
    @commands.command()
    async def echo(self, ctx: commands.Context) -> None:
        """Repeats the message given after the command.
        Will use the escaped content which does not mention anything.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        message: discord.Message = ctx.message
        await message.delete()
        if message.content:
            await ctx.send(message.clean_content[6:])

    @commands.command()
    @commands.check_any(in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
    async def flip(self, ctx: commands.Context) -> None:
        """Flips an imaginary coin and sends the result.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """

        results = ["Heads!", "Tails!"]
        outcome = random.randint(0, 1)
        await ctx.send(results[outcome])

    @commands.command()
    @commands.check_any(in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
    async def menu(self, ctx: commands.Context) -> None:
        """Sends a link to the Northeastern dining hall menu.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        await ctx.send("https://nudining.com/public/menus")


def setup(client):
    client.add_cog(Misc(client))
