import random
from discord.ext import commands
from checks import is_admin, in_channel, is_mod

from data.ids import BOT_SPAM_CHANNEL_ID


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    # replies Pong! given .ping
    @commands.command()
    @commands.check_any(in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency * 1000)}ms")

    # repeats given statement after .echo
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def echo(self, ctx, *args):
        message = ctx.message
        output = ""
        for word in args:
            output += word
            output += " "
        await message.delete()  # deletes command
        await ctx.send(output)

    # coin flip
    @commands.command()
    async def flip(self, ctx):
        outcome = random.randint(0, 1)
        if outcome == 0:
            await ctx.send("Heads!")
        else:
            await ctx.send("Tails!")

    # generates link to NU dining menu
    @commands.command()
    async def menu(self, ctx):
        await ctx.send("https://nudining.com/public/menus")

    # generates invite link to server
    @commands.command()
    async def invite(self, ctx):
        await ctx.send("discord.gg/8HHcup8")


def setup(client):
    client.add_cog(Misc(client))
