import discord
import random
from datetime import datetime
from discord.ext import commands
from checks import in_channel, is_admin, is_dm, is_mod

from data.ids import BOT_SPAM_CHANNEL_ID


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.start_time = datetime.utcnow()

    @commands.command()
    @commands.check_any(is_dm(), in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
    async def ping(self, ctx: commands.Context):
        """Sends a message which contains the Discord WebSocket protocol latency.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """

        await ctx.send(f"Pong! {round(self.client.latency * 1000)}ms")

    @commands.command()
    @commands.check_any(is_dm(), in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
    async def uptime(self, ctx: commands.Context):
        """Calculates the amount of time the bot has been up since it last started.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        delta_uptime = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"Uptime: `{days}d, {hours}h, {minutes}m, {seconds}s`")

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
        content: str = message.clean_content[6:]
        if content:
            await ctx.send(content)
        else:
            await ctx.send("You didn't give anything to repeat", delete_after=5)

    @commands.command()
    @commands.check_any(is_dm(), in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
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
    @commands.check_any(is_dm(), in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
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
