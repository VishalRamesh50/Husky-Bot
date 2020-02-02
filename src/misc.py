import discord
import random
from discord.ext import commands

from ids import BOT_SPAM_CHANNEL_ID


# if the message was sent in the BOT-SPAM CHANNEL or the author is an mod
def inBotSpam(ctx: commands.Context) -> bool:
    """
    A check to determine whether the command was called from BOT_SPAM
    or if the user is a moderator.

    Parameters
    ----------
    ctx: `commands.Context`
        A class containing metadata about the command invocation.
    
    Returns
    ----------
    True if the command was called from the BOT_SPAM_CHANNEL
    or the author is a Moderator else False.
    """
    mod: discord.Role = discord.utils.get(ctx.author.roles, name='Moderator')
    return ctx.channel.id == BOT_SPAM_CHANNEL_ID or mod


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    # replies Pong! given .ping
    @commands.command()
    @commands.check(inBotSpam)
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

    # repeats given statement after .echo
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def echo(self, ctx, *args):
        message = ctx.message
        output = ''
        for word in args:
            output += word
            output += ' '
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
        await ctx.send('https://nudining.com/public/menus')

    # generates invite link to server
    @commands.command()
    async def invite(self, ctx):
        await ctx.send('discord.gg/8HHcup8')


def setup(client):
    client.add_cog(Misc(client))
