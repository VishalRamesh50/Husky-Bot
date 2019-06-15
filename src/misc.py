import discord
from discord.ext import commands
import random

BOT_SPAM_CHANNEL_ID = 531665740521144341


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    def inBotSpam(ctx):
        return ctx.channel.id == BOT_SPAM_CHANNEL_ID

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

    # displays some server info
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def serverinfo(self, ctx):
        guild = ctx.guild
        numBots, newAccounts, online, idle, dnd, mobile = 0, 0, 0, 0, 0, 0
        for member in guild.members:
            numBots += 1 if member.bot else 0
            join_diff = (member.joined_at - member.created_at).days
            newAccounts += 1 if (join_diff <= 1) else 0
            online += 1 if (member.status == discord.Status.online) else 0
            idle += 1 if (member.status == discord.Status.idle) else 0
            dnd += 1 if (member.status == discord.Status.dnd) else 0
            mobile += 1 if member.is_on_mobile() else 0

        embed = discord.Embed(colour=discord.Colour.red(),
                              # url=guild.icon_url,
                              timestamp=guild.created_at)

        # embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=guild, icon_url=guild.icon_url)
        embed.set_footer(text=f"Server ID: {guild.id} | Server Created")

        embed.add_field(name="Server Owner", value=guild.owner.mention)
        embed.add_field(name="Region", value=guild.region)
        embed.add_field(name="Channel Categories", value=len(guild.categories))
        embed.add_field(name="Text Channels", value=len(guild.text_channels))
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels))
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Humans", value=guild.member_count - numBots)
        embed.add_field(name="Bots", value=numBots)
        embed.add_field(name="Online", value=online)
        embed.add_field(name="Idle", value=idle)
        embed.add_field(name="DnD", value=dnd)
        embed.add_field(name="Mobile", value=mobile)
        embed.add_field(name="New Accounts", value=newAccounts)
        embed.add_field(name="Emojis", value=len(guild.emojis))
        embed.add_field(name="Verification Level", value=guild.verification_level)
        embed.add_field(name="Active Invites", value=len(await guild.invites()))
        embed.add_field(name="2FA", value=bool(guild.mfa_level))

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Misc(client))
