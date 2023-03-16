import discord
from collections import Counter
from datetime import datetime
from discord.ext import commands
from typing import Optional

from client.bot import Bot
from checks import in_channel, is_admin, is_mod
from converters import FuzzyMemberConverter
from data.ids import BOT_SPAM_CHANNEL_ID
from utils import timestamp_format, member_join_position, member_mentioned_roles


class Stats(commands.Cog):
    def __init__(self, client: Bot):
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
        REGISTERED_ROLE: discord.Role = discord.utils.get(
            guild.roles, name="Registered"
        )
        new_accounts: int = Counter(
            [
                ((m.joined_at or datetime.max) - m.created_at).days <= 1
                for m in guild.members
            ]
        )[True]
        not_registered_count: int = guild.member_count - len(REGISTERED_ROLE.members)
        num_bots: int = Counter([m.bot for m in guild.members])[True]
        statuses = Counter([(m.status, m.is_on_mobile()) for m in guild.members])
        online_mobile: int = statuses[(discord.Status.online, True)]
        idle_mobile: int = statuses[(discord.Status.idle, True)]
        dnd_mobile: int = statuses[(discord.Status.dnd, True)]
        online: int = statuses[(discord.Status.online, False)] + online_mobile
        idle: int = statuses[(discord.Status.idle, False)] + idle_mobile
        dnd: int = statuses[(discord.Status.dnd, False)] + dnd_mobile

        embed = discord.Embed(color=discord.Color.red(), timestamp=guild.created_at)
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
        self, ctx: commands.Context, num: int = 10, output_type: str = "nickname"
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
        output_type: `str`
            Specifies the format of the embedded message to display the users.
            Can be: "nickname", "nick", "name", "mention"
            Nickname will give a list of nicknames
            Name will give a list of usernames
            Mention will give a list of mentioned users.
        """
        msg: str = ""
        count: int = 0
        embed = discord.Embed(
            color=discord.Color.red(), timestamp=discord.utils.utcnow()
        )
        for member in sorted(
            ctx.guild.members, key=lambda m: m.joined_at or datetime.max
        ):
            if count < num:
                if output_type == "nickname" or output_type == "nick":
                    msg += member.display_name + ", "
                elif output_type == "name":
                    msg += member.name + ", "
                elif output_type == "mention":
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
                        color=discord.Color.red(), timestamp=discord.utils.utcnow()
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

    @commands.command(aliases=["whoam"])
    @commands.guild_only()
    @commands.check_any(in_channel(BOT_SPAM_CHANNEL_ID), is_admin(), is_mod())
    async def whois(self, ctx: commands.Context, *, member_name: Optional[str] = None) -> None:
        """
        Sends an embedded message containing information about the given user.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        member_parts `Tuple`:
            The member's name as a tuple of strings.
        """
        member: Optional[discord.Member] = None
        if member_name is None or member_name.upper() == "I":
            member = ctx.author
        else:
            try:
                member = await FuzzyMemberConverter().convert(ctx, member_name)
            except discord.ext.commands.errors.BadArgument as e:
                await ctx.send(str(e))
                return

        member_permissions: discord.Permissions = ctx.author.permissions_in(ctx.channel)
        if (
            ctx.author == member
            or member_permissions.administrator
            or member_permissions.view_guild_insights
        ):
            join_position: int = member_join_position(member)
            roles: str = member_mentioned_roles(member)
            permissions: str = ""
            for perm in member.guild_permissions:
                if perm[1]:
                    perm_name = perm[0].replace("_", " ").title()
                    permissions += perm_name + ", "
            permissions = permissions[:-2]

            embed = discord.Embed(
                color=member.color,
                timestamp=discord.utils.utcnow(),
                description=member.mention,
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.set_footer(text=f"Member ID: {member.id}")
            embed.add_field(name="Status", value=member.status)
            embed.add_field(name="Joined", value=timestamp_format(member.joined_at))
            embed.add_field(name="Join Position", value=join_position)
            embed.add_field(
                name="Created At", value=timestamp_format(member.created_at)
            )
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
            member: discord.Member = sorted(
                guild.members, key=lambda m: m.joined_at or datetime.max
            )[join_no - 1]
        except IndexError:
            await ctx.send(f"{guild} only has {guild.member_count} members!")
            return
        await self.whois(ctx, member.name)


async def setup(client):
    await client.add_cog(Stats(client))
