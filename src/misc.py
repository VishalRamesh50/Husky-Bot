from discord.ext import commands
import random


class Misc:
    def __init__(self, client):
        self.client = client

    # replies Pong! given .ping
    @commands.command()
    async def ping(self):
        await self.client.say('Pong!')

    # repeats given statement after .echo
    @commands.command(pass_context=True)
    async def echo(self, ctx, *args):
        message = ctx.message
        output = ''
        for word in args:
            output += word
            output += ' '
        await self.client.delete_message(message)  # deletes command
        await self.client.say(output)

    # coin flip
    @commands.command()
    async def flip(self):
        outcome = random.randint(0, 1)
        if outcome == 0:
            await self.client.say("Heads!")
        else:
            await self.client.say("Tails!")

    # generates link to NU dining menu
    @commands.command()
    async def menu(self):
        await self.client.say('https://new.dineoncampus.com/Northeastern/menus')

    # generates invite link to server
    @commands.command()
    async def invite(self):
        await self.client.say('discord.gg/8HHcup8')


def setup(client):
    client.add_cog(Misc(client))
