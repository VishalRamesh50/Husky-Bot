import discord
from datetime import datetime, timedelta
from discord.ext import commands
from pytz import timezone
from typing import Dict, List, Union, Optional

from client.bot import Bot, ChannelType
from regex_patterns import IS_COURSE_TOPIC
from utils import required_configs, timestamp_format, member_mentioned_roles


class Logs(commands.Cog):
    """Handles everything pertained to logging discord events in server logs."""

    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    @required_configs(ChannelType.LOG)
    async def on_member_join(self, member: discord.Member) -> None:
        """Logs when a member has joined a guild.

        Parameters
        ------------
        member: `discord.Member`
            The member which has joined the guild.
        """
        ACTION_LOG_CHANNEL: discord.TextChannel = self.client.get_log_channel(
            member.guild.id
        )
        log_msg = discord.Embed(
            description=f"{member.mention} {member}",
            timestamp=discord.utils.utcnow(),
            color=discord.Color.green(),
        )
        log_msg.set_thumbnail(url=f"{member.display_avatar.url}")
        log_msg.set_author(name="Member Joined", icon_url=member.display_avatar.url)

        join_diff: Optional[timedelta] = member.joined_at and (
            member.joined_at - member.created_at
        )
        new_account_msg = "Created "
        if join_diff and join_diff.days <= 1:
            total_seconds: int = join_diff.seconds
            hours: int = total_seconds // 3600
            mins: int = (total_seconds // 60) % 60
            seconds: int = total_seconds % 60
            if hours > 0:
                new_account_msg += f"{hours} hours, "
            if mins > 0:
                new_account_msg += f"{mins} mins, "
            if seconds > 0:
                new_account_msg += f"{seconds} secs ago"
            log_msg.add_field(name="New Account", value=new_account_msg)

        log_msg.set_footer(text=f"Member ID: {member.id}")
        await ACTION_LOG_CHANNEL.send(embed=log_msg)

    @commands.Cog.listener()
    @required_configs(ChannelType.LOG)
    async def on_message_delete(self, message: discord.Message) -> None:
        """Logs any deleted messages.

        Parameters
        ------------
        message: `discord.Message`
            The message that was deleted.
        """
        guild: discord.Guild = message.guild
        ACTION_LOG_CHANNEL: discord.TextChannel = self.client.get_log_channel(guild.id)

        author: discord.Member = message.author
        channel = message.channel
        now: datetime = discord.utils.utcnow()

        if channel != ACTION_LOG_CHANNEL:
            embed = discord.Embed(
                description=f"**Message sent by {author.mention} deleted in {channel.mention}**"
                f"\n{message.content}",
                timestamp=now,
                color=discord.Color.red(),
            )
            embed.set_author(name=author, icon_url=author.display_avatar.url)

            async for entry in guild.audit_logs(
                limit=1, action=discord.AuditLogAction.message_delete
            ):
                if entry.target == author:
                    diff: int = int((now - entry.created_at).total_seconds())
                    if (
                        entry.extra.channel == channel
                        and entry.extra.count == 1
                        and diff <= 3
                    ):
                        embed.description = (
                            f"**Message sent by {author.mention} deleted by "
                            f"{entry.user.mention} in {channel.mention}**"
                            f"\n{message.content}"
                        )

            sent_at_formatted: str = f'{discord.utils.format_dt(message.created_at, "d")} {discord.utils.format_dt(message.created_at, "T")}'
            embed.add_field(
                name="Sent At",
                value=sent_at_formatted,
                inline=False,
            )
            embed.set_footer(text=f"ID: {message.id}")
            await ACTION_LOG_CHANNEL.send(embed=embed)

            for a in message.attachments:
                embed = discord.Embed(
                    title="Deleted Attachment",
                    description=f"**Attachment sent by {author.mention} deleted in {channel.mention}**",
                    timestamp=discord.utils.utcnow(),
                    color=discord.Color.red(),
                )
                embed.set_image(url=a.proxy_url)
                embed.add_field(
                    name="Cached URL", value=f"[{a.filename}]({a.proxy_url})"
                )
                await ACTION_LOG_CHANNEL.send(embed=embed)

    @commands.Cog.listener()
    @required_configs(ChannelType.LOG)
    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        """Logs the before & after state of an edited message.

        Parameters
        ------------
        before: `discord.Message`
            The message object before the edit.
        after: `discord.Message`
            The message object after the edit.
        """
        before_content: str = before.content
        after_content: str = after.content

        # check that content has changed because this event
        # could be called even if the content hasn't changed
        if before_content != after_content:
            ACTION_LOG_CHANNEL: discord.TextChannel = self.client.get_log_channel(
                before.guild.id
            )
            author: discord.Member = before.author
            channel: discord.TextChannel = before.channel
            embed = discord.Embed(
                description=f"**[Message edited in]({after.jump_url}){channel.mention}**",
                timestamp=discord.utils.utcnow(),
                color=discord.Color.gold(),
            )
            embed.set_author(name=author, icon_url=author.display_avatar.url)
            if before_content == "":
                before_content = "<No content>"
            elif len(before_content) > 1024:
                before_content = before_content[:1020] + "..."
            embed.add_field(name="Before", value=before_content, inline=False)
            if after_content == "":
                before_content = "<No content>"
            elif len(after_content) > 1024:
                after_content = after_content[:1020] + "..."
            embed.add_field(name="After", value=after_content, inline=False)

            last_edited_or_sent_at: datetime = before.edited_at or before.created_at
            last_edited_or_sent_at_formatted: str = f'{discord.utils.format_dt(last_edited_or_sent_at, "d")} {discord.utils.format_dt(last_edited_or_sent_at, "T")}'
            embed.add_field(
                name="Last Edited/Sent",
                value=last_edited_or_sent_at_formatted,
                inline=False,
            )
            embed.set_footer(text=f"User ID: {author.id}")
            await ACTION_LOG_CHANNEL.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        """Logs when a user has changed their profile picture and what it was.

        Parameters
        ------------
        before: `discord.User`
            The user object before the update.
        after: `discord.User`
            The user object after the update.
        """
        if before.bot:
            return

        if before.display_avatar.url != after.display_avatar.url:
            action_log_channels: List[discord.TextChannel] = []
            for guild in after.mutual_guilds:
                channel: Optional[discord.TextChannel] = self.client.get_log_channel(
                    guild.id
                )
                if channel:
                    action_log_channels.append(channel)

            if len(action_log_channels) == 0:
                return

            embed = discord.Embed(
                description="Profile Picture Changed",
                timestamp=discord.utils.utcnow(),
                color=discord.Color.gold(),
            )
            embed.set_author(name=after, icon_url=after.display_avatar.url)
            embed.set_image(url=after.display_avatar.url)
            embed.set_thumbnail(url=before.display_avatar.url)
            embed.set_footer(text=f"User ID: {after.id}")
            for channel in action_log_channels:
                await channel.send(embed=embed)

    @commands.Cog.listener()
    @required_configs(ChannelType.LOG)
    async def on_member_remove(self, member: discord.Member) -> None:
        """Handles the logging of when a member leaves a guild.
        This can be from an optional leave, a kick, or a ban.

        Parameters
        ------------
        member: `discord.Member`
            The member which has left the guild.
        """

        guild: discord.Guild = member.guild
        ACTION_LOG_CHANNEL: discord.TextChannel = self.client.get_log_channel(guild.id)

        roles: str = member_mentioned_roles(member)
        log_msg = discord.Embed(
            timestamp=discord.utils.utcnow(), color=discord.Color.red()
        )
        log_msg.add_field(name=member, value=member.mention)
        log_msg.set_thumbnail(url=member.display_avatar.url)
        log_msg.set_author(name="Member Left", icon_url=member.display_avatar.url)
        log_msg.add_field(name="Joined At", value=timestamp_format(member.joined_at))
        log_msg.add_field(name="Created At", value=timestamp_format(member.created_at))
        log_msg.set_footer(text=f"Member ID: {member.id}")

        async for entry in guild.audit_logs(limit=5):
            if entry.target == member:
                if entry.action == discord.AuditLogAction.ban:
                    log_msg.set_author(
                        name="Member Banned", icon_url=member.display_avatar.url
                    )
                    log_msg.add_field(name="Moderator", value=entry.user)
                    log_msg.add_field(name="Reason", value=str(entry.reason))
                    break
                elif entry.action == discord.AuditLogAction.kick:
                    log_msg.set_author(
                        name="Member Kicked", icon_url=member.display_avatar.url
                    )
                    log_msg.add_field(name="Moderator", value=entry.user)
                    log_msg.add_field(name="Reason", value=str(entry.reason))
                    break

        log_msg.add_field(name=f"Roles ({len(member.roles) - 1})", value=roles)
        await ACTION_LOG_CHANNEL.send(embed=log_msg)

    @commands.Cog.listener()
    @required_configs(ChannelType.LOG)
    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ) -> None:
        """Logs when a member has enrolled in or unenrolled from a course.

        Parameters
        -----------
        before: `discord.abc.GuildChannel`
            The channel before.
        after: `discord.abc.GuildChannel`
            The channel after.
        """
        if not isinstance(after, discord.TextChannel):
            return

        if before.topic is None or after.topic is None:
            return

        if not IS_COURSE_TOPIC.match(before.topic) or not IS_COURSE_TOPIC.match(
            after.topic
        ):
            return

        before_overwrites_len: int = len(before.overwrites)
        after_overwrites_len: int = len(after.overwrites)
        if before_overwrites_len == after_overwrites_len:
            return

        changed_key: Optional[Union[discord.Role, discord.Member]] = next(
            iter(after.overwrites.keys() ^ before.overwrites.keys()), None
        )
        if not isinstance(changed_key, discord.Member):
            return

        ACTION_LOG_CHANNEL: discord.TextChannel = self.client.get_log_channel(
            before.guild.id
        )
        if after_overwrites_len > before_overwrites_len:
            embed = discord.Embed(
                timestamp=discord.utils.utcnow(), color=discord.Color.green()
            )
            embed.set_author(
                name="Course Enrolled", icon_url=changed_key.display_avatar.url
            )
        elif after_overwrites_len < before_overwrites_len:
            embed = discord.Embed(
                timestamp=discord.utils.utcnow(), color=discord.Color.red()
            )
            embed.set_author(
                name="Course Unenrolled", icon_url=changed_key.display_avatar.url
            )
        embed.add_field(name=changed_key, value=changed_key.mention)
        embed.add_field(name="Details", value=after.topic)
        embed.add_field(name="Channel", value=after.mention)
        embed.set_footer(text=f"Member ID: {changed_key.id}")
        await ACTION_LOG_CHANNEL.send(embed=embed)

    @commands.Cog.listener()
    @required_configs(ChannelType.LOG)
    async def on_invite_create(self, invite: discord.Invite) -> None:
        """Logs when a new invite link has been created.

        Parameters
        -----------
        invite: `discord.Invite`
            The invite created.
        """
        if (
            invite.guild is None
            or invite.inviter is None
            or invite.channel is None
            or invite.max_age is None
        ):
            return

        ACTION_LOG_CHANNEL: discord.TextChannel = self.client.get_log_channel(
            invite.guild.id
        )
        inviter: discord.User = invite.inviter
        invite_channel: Union[
            discord.abc.GuildChannel, discord.Object, discord.PartialInviteChannel
        ] = invite.channel
        try:
            if (
                invite_channel.type == discord.ChannelType.text
                or invite_channel.type == discord.ChannelType.news
            ):
                channel: str = invite_channel.mention
            elif invite_channel.type == discord.ChannelType.voice:
                channel = f"🔊{invite_channel.name}"
        except AttributeError:
            channel = invite_channel

        max_age: str = "Never"
        time_map: Dict[str, int] = {"day(s)": 86400, "hour(s)": 3600, "minute(s)": 60}
        for unit_of_time, seconds in time_map.items():
            result: int = invite.max_age // seconds
            if result:
                max_age = f"{result} {unit_of_time}"
                break

        embed = discord.Embed(
            timestamp=discord.utils.utcnow(), color=discord.Color.green()
        )
        embed.set_author(name="New Invite Created", icon_url=inviter.display_avatar.url)
        embed.add_field(name=inviter, value=inviter.mention)
        embed.add_field(name="Code", value=invite.code)
        embed.add_field(name="Channel", value=channel)
        embed.add_field(name="Max Uses", value=invite.max_uses or "Unlimited")
        embed.add_field(name="Expires After", value=max_age)
        embed.add_field(name="Temporary", value=invite.temporary)
        await ACTION_LOG_CHANNEL.send(embed=embed)


async def setup(client):
    await client.add_cog(Logs(client))
