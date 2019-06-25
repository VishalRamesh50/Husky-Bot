from discord.ext import commands
import random

BOT_SPAM_CHANNEL_ID = 531665740521144341


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    # if the message was sent in the BOT_SPAM_CHANNEL or the author is an admin
    def inBotSpam(ctx):
        # if user has an administrator permissions
        admin = ctx.author.permissions_in(ctx.channel).administrator
        return ctx.channel.id == BOT_SPAM_CHANNEL_ID or admin

    # replies Pong! given .ping
    @commands.command()
    @commands.check(inBotSpam)
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

    # repeats given statement after .echo
    @commands.command()
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
        await ctx.send('https://new.dineoncampus.com/Northeastern/menus')

    # generates invite link to server
    @commands.command()
    async def invite(self, ctx):
        await ctx.send('discord.gg/8HHcup8')


def setup(client):
    client.add_cog(Misc(client))
