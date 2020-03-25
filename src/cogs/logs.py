import discord
from datetime import datetime
from discord.ext import commands
from pytz import timezone

from data.ids import ACTION_LOG_CHANNEL_ID


class Logs(commands.Cog):
    def __init__(self, client):
        self.client = client

    # logs when a user has joined the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        EST = datetime.now(timezone("US/Eastern"))  # EST timezone
        ACTION_LOG_CHANNEL = self.client.get_channel(ACTION_LOG_CHANNEL_ID)
        # send a message in the logs about the details
        log_msg = discord.Embed(
            description=f"{member.mention} {member}",
            timestamp=EST,
            colour=discord.Colour.green(),
        )
        log_msg.set_thumbnail(url=f"{member.avatar_url}")
        log_msg.set_author(name="Member Joined", icon_url=member.avatar_url)
        join_diff = member.joined_at - member.created_at
        new_account_msg = "Created "
        if join_diff.days <= 1:
            seconds = join_diff.seconds
            hours = seconds // 3600
            mins = (seconds // 60) % 60
            seconds = seconds % 60
            if hours > 0:
                new_account_msg += f"{hours} hours, "
            if mins > 0:
                new_account_msg += f"{mins} mins, "
            if seconds > 0:
                new_account_msg += f"{seconds} secs ago"
            log_msg.add_field(name="New Account", value=new_account_msg)
        log_msg.set_footer(text=f"Member ID: {member.id}")
        await ACTION_LOG_CHANNEL.send(embed=log_msg)

    # says what message was deleted and by whom
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        EST = datetime.now(timezone("US/Eastern"))  # EST timezone
        ACTION_LOG_CHANNEL = self.client.get_channel(ACTION_LOG_CHANNEL_ID)
        author = message.author
        isBot = author.bot  # if the author of the message is a bot
        if not isBot:
            try:
                content = message.content
                channel = message.channel
                attachments = message.attachments
                embed = discord.Embed(
                    description=f"**Message sent by {author.mention} deleted in {channel.mention}**\n {content}",
                    timestamp=EST,
                    colour=discord.Colour.red(),
                )
                embed.set_author(name=author, icon_url=author.avatar_url)
                embed.set_footer(text=f"ID: {message.id}")
                await ACTION_LOG_CHANNEL.send(embed=embed)

                for a in attachments:
                    embed = discord.Embed(
                        title="Deleted Attachment",
                        description=f"**Attachment sent by {author.mention} deleted in {channel.mention}**\n",
                        timestamp=EST,
                        colour=discord.Colour.red(),
                    )
                    embed.set_image(url=a.proxy_url)
                    embed.add_field(name="Cached URL", value=f"[Link]({a.proxy_url})")
                    await ACTION_LOG_CHANNEL.send(embed=embed)
            except discord.errors.HTTPException as e:
                print(e)

    # displays before & after state of edited message
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        EST = datetime.now(timezone("US/Eastern"))  # EST timezone
        ACTION_LOG_CHANNEL = self.client.get_channel(ACTION_LOG_CHANNEL_ID)
        author = before.author
        channel = before.channel
        before_content = before.content
        after_content = after.content
        if before_content != after_content:
            try:
                embed = discord.Embed(
                    description=f"**[Message edited in]({after.jump_url}){channel.mention}**",
                    timestamp=EST,
                    colour=discord.Colour.gold(),
                )
                embed.set_author(name=author, icon_url=author.avatar_url)
                embed.add_field(name="Before", value=before_content, inline=False)
                embed.add_field(name="After", value=after_content, inline=False)
                embed.set_footer(text=f"User ID: {author.id}")
                await ACTION_LOG_CHANNEL.send(embed=embed)
            except discord.errors.HTTPException as e:
                print(e)

    @commands.Cog.listener()
    async def on_user_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        """Logs when a user has changed their profile picture and what it was.

        Parameters
        ------------
        before: `discord.Member`
            The member object before the update.
        after: `discord.Member`
            The member object after the update.
        """

        ACTION_LOG_CHANNEL: discord.TextChannel = after.guild.get_channel(
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
