import discord
from discord.ext import commands
import random

BOT_SPAM_CHANNEL_ID = 531665740521144341
COURSE_REGISTRATION_CHANNEL_ID = 485279507582943262


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    # if the message was sent in the BOT_SPAM_CHANNEL or the author is an admin
    def inBotSpam(ctx):
        # if user has an administrator permissions
        admin = ctx.author.permissions_in(ctx.channel).administrator
        return ctx.channel.id == BOT_SPAM_CHANNEL_ID or admin

    # if the message was sent in the COURSE_REGISTRATION_CHANNEL or the author is an admin
    def inCourseRegistration(ctx):
        # if user has an administrator permissions
        admin = ctx.author.permissions_in(ctx.channel).administrator
        return ctx.channel.id == COURSE_REGISTRATION_CHANNEL_ID or admin

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

    # returns a lower-case string without dashes and stripping whitespace
    def ignoreDashCase(self, input):
        return ' '.join(input.split('-')).lower().strip()

    # toggles course registration roles
    @commands.command()
    @commands.check(inCourseRegistration)
    async def choose(self, ctx, *args):
        message = ctx.message
        guild = ctx.guild
        member = message.author
        admin = member.permissions_in(ctx.channel).administrator
        await message.delete()
        args = ' '.join(args).strip()
        role = None
        try:
            role = await commands.RoleConverter().convert(ctx, args)
        except discord.ext.commands.errors.BadArgument as e:
            for r in guild.roles:
                if (args.lower() == r.name.lower() or
                   self.ignoreDashCase(args) == self.ignoreDashCase(r.name)):
                    role = r
                    break
            if role is None:
                await ctx.send(e, delete_after=5)
                return
        WHITELISTED_COLLEGES = ['CCIS', 'COE', 'BCHS', 'CAMD', 'DMSB', 'COS', 'CSSH', 'EXPLORE']
        WHITELISTED_COLORS = ['ORANGE', 'LIGHT GREEN', 'YELLOW', 'PURPLE', 'LIGHT BLUE', 'PINK', 'LIGHT PINK', 'PALE PINK', 'CYAN', 'SPRING GREEN', 'PALE YELLOW']
        if ('-' in role.name or role.name in WHITELISTED_COLLEGES + WHITELISTED_COLORS or admin):
            if (role in member.roles):
                try:
                    await member.remove_roles(role)
                    await ctx.send(f"{role.name} has been removed", delete_after=5)
                except discord.errors.Forbidden:
                    await ctx.send("I do not have permission to alter that role", delete_after=5)
            else:
                try:
                    await member.add_roles(role)
                    await ctx.send(f"{role.name} has been added!", delete_after=5)
                except discord.errors.Forbidden:
                    await ctx.send("I do not have permission to alter that role", delete_after=5)
        else:
            await ctx.send("You do not have the permission to toggle that role 🙃", delete_after=5)


def setup(client):
    client.add_cog(Misc(client))
