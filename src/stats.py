import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone

BOT_SPAM_CHANNEL_ID = 531665740521144341


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.EST = datetime.now(timezone('US/Eastern'))  # EST timezone

    # if the message was sent in the BOT_SPAM_CHANNEL or the author is an admin
    def inBotSpam(ctx):
        # if user has an administrator permissions
        admin = ctx.author.permissions_in(ctx.channel).administrator
        return ctx.channel.id == BOT_SPAM_CHANNEL_ID or admin

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

    # displays a list of a given number of members ordered by join date
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def orderedListMembers(self, ctx, num=10):
        try:
            num = int(num)
        except ValueError:
            await ctx.send("Provide a valid integer.")
            return
        allMembers = ctx.guild.members
        sortedMembers = sorted(allMembers, key=lambda m: m.joined_at)
        msg = ""
        count = 0
        embed = discord.Embed(colour=discord.Color.red(), timestamp=self.EST)
        for member in sortedMembers:
            if (count < num):
                msg += member.mention + ", "
                count += 1
                # if there are at least 10 members
                if (len(sortedMembers) >= 10):
                    # if 10 members were reached add to the message
                    if (count % 10 == 0):
                        embed.add_field(name=f"__{count - 9}-{count}:__", value=msg[:len(msg)-2])
                        msg = ""
                    # if 100 members were reached send the embed and reset it to start a new one
                    if (count % 100 == 0):
                        await ctx.send(embed=embed)
                        embed = discord.Embed(colour=discord.Color.red(), timestamp=self.EST)
        # if an even 10 people was not reached
        if (msg != ""):
            embed.add_field(name=f"__{count - count % 10 + 1}-{count}:__", value=msg[:len(msg)-2])
            await ctx.send(embed=embed)

    # format a date with Day, Month Date, Year Hour: Minute: Seconds removing 0 padding
    def formatDate(self, input):
        return input.strftime("%a, %b %d, %Y %I:%M:%S %p").replace(" 0", " ")

    # displays some information about a user who joined the server at the join position
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def joinNo(self, ctx, num):
        self.__init__(self.client)  # re-initialize variables
        guild = ctx.guild
        allMembers = guild.members
        try:
            num = int(num)
        except ValueError:
            await ctx.send("Enter a valid integer.")
            return
        if (num <= 0):
            await ctx.send("Number must be a positive non-zero number.")
            return
        sortedMembers = sorted(allMembers, key=lambda m: m.joined_at)
        if num <= len(sortedMembers):
            member = sortedMembers[num-1]
        else:
            await ctx.send(f"{guild} only has {guild.member_count} members!")
            return
        roles = ''
        for role in member.roles[1:]:
            roles += role.mention + ' '
        # display NO ROLES if user has no roles
        roles = 'NO ROLES' if roles == '' else roles
        permissions = ''
        for perm in member.guild_permissions:
            name = perm[0].replace('_', ' ').title()
            value = perm[1]
            if value:
                permissions += (name + ', ')
        permissions = permissions[:-2]
        embed = discord.Embed(colour=member.color, timestamp=self.EST, description=member.mention)

        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=member.name + '#' + member.discriminator, icon_url=member.avatar_url)
        embed.set_footer(text=f"Member ID: {member.id}")

        embed.add_field(name="Status", value=member.status)
        embed.add_field(name="Joined", value=self.formatDate(member.joined_at))
        embed.add_field(name="Join Position", value=num)
        embed.add_field(name="Created At", value=self.formatDate(member.created_at))
        embed.add_field(name=f"Roles ({len(member.roles) - 1})", value=roles)
        embed.add_field(name="Key Permissions", value=permissions)

        await ctx.send(embed=embed)

    # displays some information about a given member
    @commands.command()
    @commands.check(inBotSpam)
    async def whois(self, ctx, member: discord.Member):
        self.__init__(self.client)  # re-initialize variables
        # if user has an administrator permissions
        admin = ctx.author.permissions_in(ctx.channel).administrator
        if ctx.author == member or admin:
            allMembers = ctx.guild.members
            sortedMembers = sorted(allMembers, key=lambda m: m.joined_at)
            joinPosition = sortedMembers.index(member) + 1
            roles = ''
            for role in member.roles[1:]:
                roles += role.mention + ' '
            # display NO ROLES if user has no roles
            roles = 'NO ROLES' if roles == '' else roles
            permissions = ''
            for perm in member.guild_permissions:
                name = perm[0].replace('_', ' ').title()
                value = perm[1]
                if value:
                    permissions += (name + ', ')
            permissions = permissions[:-2]
            embed = discord.Embed(colour=member.color, timestamp=self.EST, description=member.mention)

            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=member.name + '#' + member.discriminator, icon_url=member.avatar_url)
            embed.set_footer(text=f"Member ID: {member.id}")
            embed.add_field(name="Status", value=member.status)
            embed.add_field(name="Joined", value=self.formatDate(member.joined_at))
            embed.add_field(name="Join Position", value=joinPosition)
            embed.add_field(name="Created At", value=self.formatDate(member.created_at))
            embed.add_field(name=f"Roles ({len(member.roles) - 1})", value=roles)
            embed.add_field(name="Key Permissions", value=permissions)

            await ctx.send(embed=embed)
        else:
            await ctx.message.delete()
            await ctx.send("Stop snooping around where you shouldn't 🙃", delete_after=5)


def setup(client):
    client.add_cog(Stats(client))
