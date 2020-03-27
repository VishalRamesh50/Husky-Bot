import discord
from datetime import datetime, timedelta
from discord.ext import commands
from pytz import timezone

from data.ids import ACTION_LOG_CHANNEL_ID


class Logs(commands.Cog):
    """Handles everything pertained to logging discord events in server logs."""

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Logs when a member has joined a guild.

        Parameters
        ------------
        member: `discord.Member`
            The member which has joined the guild.
        """

        ACTION_LOG_CHANNEL: discord.TextChannel = member.guild.get_channel(
            ACTION_LOG_CHANNEL_ID
        )
        log_msg = discord.Embed(
            description=f"{member.mention} {member}",
            timestamp=datetime.utcnow(),
            colour=discord.Colour.green(),
        )
        log_msg.set_thumbnail(url=f"{member.avatar_url}")
        log_msg.set_author(name="Member Joined", icon_url=member.avatar_url)

        join_diff: timedelta = member.joined_at - member.created_at
        new_account_msg = "Created "
        if join_diff.days <= 1:
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
    async def on_message_delete(self, message: discord.Message) -> None:
        """Logs any deleted messages.

        Parameters
        ------------
        message: `discord.Message`
            The message that was deleted.
        """

        guild: discord.Guild = message.guild
        ACTION_LOG_CHANNEL: discord.TextChannel = guild.get_channel(
            ACTION_LOG_CHANNEL_ID
        )
        author: discord.Member = message.author
        channel: discord.TextChannel = message.channel
        now: datetime = datetime.utcnow()

        if channel != ACTION_LOG_CHANNEL:
            utc_sent: datetime = timezone("UTC").localize(message.created_at)
            est_sent: datetime = utc_sent.astimezone(timezone("US/Eastern"))
            embed = discord.Embed(
                description=f"**Message sent by {author.mention} deleted in {channel.mention}**"
                f"\n{message.content}",
                timestamp=now,
                colour=discord.Colour.red(),
            )
            embed.set_author(name=author, icon_url=author.avatar_url)

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

            embed.add_field(
                name="Sent At", value=est_sent.strftime("%x %I:%M%p"), inline=False,
            )
            embed.set_footer(text=f"ID: {message.id}")
            await ACTION_LOG_CHANNEL.send(embed=embed)

            for a in message.attachments:
                embed = discord.Embed(
                    title="Deleted Attachment",
                    description=f"**Attachment sent by {author.mention} deleted in {channel.mention}**",
                    timestamp=datetime.utcnow(),
                    colour=discord.Colour.red(),
                )
                embed.set_image(url=a.proxy_url)
                embed.add_field(
                    name="Cached URL", value=f"[{a.filename}]({a.proxy_url})"
                )
                await ACTION_LOG_CHANNEL.send(embed=embed)

    @commands.Cog.listener()
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

        ACTION_LOG_CHANNEL: discord.TextChannel = after.channel.guild.get_channel(
            ACTION_LOG_CHANNEL_ID
        )
        author: discord.Member = before.author
        channel: discord.TextChannel = before.channel
        before_content: str = before.content
        after_content: str = after.content

        # check that content has changed because this event
        # could be called even if the content hasn't changed
        if before_content != after_content:
            embed = discord.Embed(
                description=f"**[Message edited in]({after.jump_url}){channel.mention}**",
                timestamp=datetime.utcnow(),
                colour=discord.Colour.gold(),
            )
            embed.set_author(name=author, icon_url=author.avatar_url)
            embed.add_field(name="Before", value=before_content, inline=False)
            embed.add_field(name="After", value=after_content, inline=False)
            utc_last_edited: datetime = timezone("UTC").localize(
                before.edited_at or before.created_at
            )
            est_last_edited: datetime = utc_last_edited.astimezone(
                timezone("US/Eastern")
            )
            embed.add_field(
                name="Last Edited/Sent",
                value=est_last_edited.strftime("%x %I:%M%p"),
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
        after: `discord.user`
            The user object after the update.
        """

        ACTION_LOG_CHANNEL: discord.TextChannel = self.client.get_channel(
            ACTION_LOG_CHANNEL_ID
        )

        if before.avatar_url != after.avatar_url:
            embed = discord.Embed(
                description="Profile Picture Changed",
                timestamp=datetime.utcnow(),
                colour=discord.Colour.gold(),
            )
            embed.set_author(name=after, icon_url=after.avatar_url)
            embed.set_image(url=after.avatar_url)
            embed.set_thumbnail(url=before.avatar_url)
            embed.set_footer(text=f"User ID: {after.id}")
            await ACTION_LOG_CHANNEL.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Handles the logging of when a member leaves a guild.
        This can be from an optional leave, a kick, or a ban.

        Parameters
        ------------
        member: `discord.Member`
            The member which has left the guild.
        """

        guild: discord.Guild = member.guild
        ACTION_LOG_CHANNEL: discord.TextChannel = guild.get_channel(
            ACTION_LOG_CHANNEL_ID
        )

        log_msg = discord.Embed(
            timestamp=datetime.utcnow(), colour=discord.Colour.red(),
        )
        log_msg.add_field(name=member, value=member.mention)
        log_msg.set_thumbnail(url=member.avatar_url)
        log_msg.set_author(name="Member Left", icon_url=member.avatar_url)
        utc_joined_at: datetime = timezone("UTC").localize(member.joined_at)
        est_joined_at: datetime = utc_joined_at.astimezone(timezone("US/Eastern"))
        log_msg.add_field(
            name="Joined At", value=est_joined_at.strftime("%x %I:%M%p"), inline=False,
        )
        log_msg.set_footer(text=f"Member ID: {member.id}")

        async for entry in guild.audit_logs(limit=5):
            if entry.target == member:
                if entry.action == discord.AuditLogAction.ban:
                    log_msg.set_author(name="Member Banned", icon_url=member.avatar_url)
                    log_msg.add_field(name="Moderator", value=entry.user)
                    break
                elif entry.action == discord.AuditLogAction.kick:
                    log_msg.set_author(name="Member Kicked", icon_url=member.avatar_url)
                    log_msg.add_field(name="Moderator", value=entry.user)
                    break

        await ACTION_LOG_CHANNEL.send(embed=log_msg)


def setup(client):
    client.add_cog(Logs(client))
