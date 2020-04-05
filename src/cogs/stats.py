import discord
from collections import Counter
from datetime import datetime
from discord.ext import commands
from pytz import timezone

from checks import is_admin, in_channel, is_mod
from data.ids import BOT_SPAM_CHANNEL_ID


class Stats(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    @commands.guild_only()
    @commands.check_any(is_admin(), is_mod())
    async def serverinfo(self, ctx: commands.Context) -> None:
        """
        Sends an embedded message containing some stats about the server.
        Includes: Server ID, Server Owner, Region,
        Num of Channel Categories, Text Channels, Voice Channels, Roles, Members,
        Humans, Bots, Online/Idle/Dnd Members, Not Registered, New Accounts, Emojis,
        Verification Level, Active Invites, 2FA Status

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.

        Note: A New Account is considered to be an account which was created within 1 day of joining the server.
        """
        guild: discord.Guild = ctx.guild
        NOT_REGISTERED: discord.Role = discord.utils.get(
            guild.roles, name="Not Registered"
        )
        new_accounts: int = Counter(
            [(m.joined_at - m.created_at).days <= 1 for m in guild.members]
        )[True]
        not_registered_count: int = Counter(
            [NOT_REGISTERED in m.roles for m in guild.members]
        )[True]
        num_bots: int = Counter([m.bot for m in guild.members])[True]
        statuses = Counter([(m.status, m.is_on_mobile()) for m in guild.members])
        online_mobile: int = statuses[(discord.Status.online, True)]
        idle_mobile: int = statuses[(discord.Status.idle, True)]
        dnd_mobile: int = statuses[(discord.Status.dnd, True)]
        online: int = statuses[(discord.Status.online, False)] + online_mobile
        idle: int = statuses[(discord.Status.idle, False)] + idle_mobile
        dnd: int = statuses[(discord.Status.dnd, False)] + dnd_mobile
        return

        embed = discord.Embed(colour=discord.Colour.red(), timestamp=guild.created_at)
        embed.set_author(name=guild, icon_url=guild.icon_url)
        embed.set_footer(text=f"Server ID: {guild.id} | Server Created")

        embed.add_field(name="Server Owner", value=guild.owner.mention)
        embed.add_field(name="Region", value=guild.region)
        embed.add_field(name="Channel Categories", value=len(guild.categories))
        embed.add_field(name="Text Channels", value=len(guild.text_channels))
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels))
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Humans", value=guild.member_count - num_bots)
        embed.add_field(name="Bots", value=num_bots)
        embed.add_field(name="Online", value=f"{online} | Mobile: {online_mobile}")
        embed.add_field(name="Idle", value=f"{idle} | Mobile: {idle_mobile}")
        embed.add_field(name="Dnd", value=f"{dnd} | Mobile: {dnd_mobile}")
        embed.add_field(name="Not Registered", value=not_registered_count)
        embed.add_field(name="New Accounts", value=new_accounts)
        embed.add_field(name="Emojis", value=f"{len(guild.emojis)}/{guild.emoji_limit}")
        embed.add_field(name="Verification Level", value=guild.verification_level)
        embed.add_field(name="Active Invites", value=len(await guild.invites()))
        embed.add_field(name="2FA", value=bool(guild.mfa_level))

        await ctx.send(embed=embed)

    @commands.command(
        aliases=["orderedListMembers", "lsMembers", "listMembers", "list_members"]
    )
    @commands.guild_only()
    @commands.check_any(is_admin(), is_mod())
    async def ordered_list_members(
        self, ctx: commands.Context, num: int = 10, outputType: str = "nickname"
    ) -> None:
        """
        Sends an embedded message containing a list of members in order by
        when the joined the server.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        num: `int`
            An integer representing the number of members to be displayed.
        outputType: `str`
            Specifies the format of the embedded message to display the users.
            Can be: "nickname", "nick", "name", "mention"
            Nickname will give a list of nicknames
            Name will give a list of usernames
            Mention will give a list of mentioned users.
        """
        msg: str = ""
        count: int = 0
        embed = discord.Embed(colour=discord.Color.red(), timestamp=datetime.utcnow())
        for member in sorted(ctx.guild.members, key=lambda m: m.joined_at):
            if count < num:
                if outputType == "nickname" or outputType == "nick":
                    msg += member.display_name + ", "
                elif outputType == "name":
                    msg += member.name + ", "
                elif outputType == "mention":
                    msg += member.mention + ", "
                else:
                    await ctx.send(
                        "Valid display type not given. Try: nickname/nick/name/mention"
                    )
                    return
                count += 1
                if count % 10 == 0:
                    embed.add_field(name=f"__{count - 9}-{count}:__", value=msg[:-2])
                    msg = ""
                if count % 100 == 0:
                    await ctx.send(embed=embed)
                    embed = discord.Embed(
                        colour=discord.Color.red(), timestamp=datetime.utcnow()
                    )
        # if an even 10 people was not reached
        if msg != "":
            embed.add_field(
                name=f"__{count - (count % 10) + 1}-{count}:__", value=msg[:-2]
            )
            await ctx.send(embed=embed)
        # if less than 100 members was reached
        elif msg == "":
            await ctx.send(embed=embed)

    # format a date with Day, Month Date, Year Hour: Minute: Seconds removing 0 padding
    def formatDate(self, input):
        return input.strftime("%a, %b %d, %Y %I:%M:%S %p").replace(" 0", " ")

    # displays some information about a given member
    @commands.command(aliases=['whoam'])
    @commands.check_any(in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
    async def whois(self, ctx: commands.Context, *args) -> None:
        """
        Sends an embedded message containing information about the given user.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        *args:
            The arguments to the command, ideally a member name.
        """
        member = None
        args = ' '.join(args)
        # if no argument was given or I was given set member to the user calling the command
        if args == '' or args.upper() == 'I':
            member = ctx.author
        else:
            # try to convert the argument into a valid member
            try:
                member = await commands.MemberConverter().convert(ctx, args)
            # if unable to convert argument to a member
            except discord.ext.commands.errors.BadArgument as e:
                for m in ctx.guild.members:
                    # if the given arguments are part of a valid member's name or nickname
                    if args.lower() in m.display_name.lower() or args.lower() in m.name.lower():
                        member = m
                        break
                # if member has still not been assigned send error message
                if member is None:
                    await ctx.send(e)
                    return
        EST = datetime.now(timezone('US/Eastern'))  # EST timezone
        # if user has an administrator permissions
        admin = ctx.author.permissions_in(ctx.channel).administrator
        mod = discord.utils.get(ctx.author.roles, name='Moderator')
        if ctx.author == member or admin or mod:
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
            embed = discord.Embed(colour=member.color, timestamp=EST, description=member.mention)

            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=member, icon_url=member.avatar_url)
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

    @commands.command(aliases=["joinNo", "joinPosition", "joinPos"])
    @commands.guild_only()
    @commands.check_any(is_admin(), is_mod())
    async def join_no(self, ctx: commands.Context, join_no: int) -> None:
        """
        Sends an embedded message containing information about the user who joined
        the server at the given join position.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        join_no: `int`
            The join position of the user to get information about.
        """
        guild: discord.Guild = ctx.guild
        if join_no <= 0:
            await ctx.send("Number must be a positive non-zero number.")
            return
        try:
            member: discord.Member = sorted(guild.members, key=lambda m: m.joined_at)[
                join_no - 1
            ]
        except IndexError:
            await ctx.send(f"{guild} only has {guild.member_count} members!")
            return
        await self.whois(ctx, member.name)


def setup(client):
    client.add_cog(Stats(client))
