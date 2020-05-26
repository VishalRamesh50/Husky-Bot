import discord
import re
from discord.ext import commands
from typing import Optional

from checks import is_admin, in_channel
from converters import CaseInsensitiveRoleConverter, CourseChannelConverter
from data.ids import COURSE_REGISTRATION_CHANNEL_ID, ADMIN_CHANNEL_ID
from .regex_patterns import IS_COURSE_TOPIC


class CourseSelection(commands.Cog):
    """Handles the interaction surrounding selecting courses or other roles
    from course-regisration via commands and clean-up.

    Attributes
    ------------
    delete_self_message: `bool`
        Flag to determine whether to delete message sent by itself in the
        course-registration channel or not.
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.delete_self_message: bool = True

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ) -> None:
        """Updates course enrollment count when a member joins or leaves.

        Parameters
        -----------
        before: `discord.abc.GuildChannel`
            The channel before.
        after: `discord.abc.GuildChannel`
            The channel after.
        """
        if not isinstance(after, discord.TextChannel):
            return

        if not IS_COURSE_TOPIC.match(before.topic) or not IS_COURSE_TOPIC.match(
            after.topic
        ):
            return

        if before.overwrites == after.overwrites:
            return

        await after.edit(
            topic=re.sub(r"\(\d+", f"({len(after.overwrites) - 1}", after.topic)
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Deletes any message sent within 5 seconds in the course-registration channel.
        Will delete messages sent by itself when the delete_self_message flag is True,
        else it will not.

        Parameters
        -----------
        message: `discord.Message`
            The sent message.
        """
        channel: discord.TextChannel = message.channel
        if channel.id == COURSE_REGISTRATION_CHANNEL_ID:
            author: discord.Member = message.author
            admin: bool = author.permissions_in(channel).administrator
            if self.delete_self_message and author == self.client.user:
                await message.delete(delay=5)
            elif not admin and author != self.client.user:
                await message.delete(delay=5)

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["toggleAD"])
    async def toggle_ad(self, ctx: commands.Context) -> None:
        """Toggles the delete_self_message flag."""
        self.delete_self_message = not self.delete_self_message
        await ctx.send(
            f"Deleting self-messages was toggled to: {self.delete_self_message}"
        )

    @commands.command()
    @commands.guild_only()
    @commands.check_any(in_channel(COURSE_REGISTRATION_CHANNEL_ID), is_admin())
    async def choose(self, ctx: commands.Context, *, name: str) -> None:
        """Command to add or remove any roles from the person invoking the command.
        If the author is not an admin, they can only toggle roles which are available
        in the course-registration channel.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        name: `str`
            The name of the role/course to be toggled.
        """
        message: discord.Message = ctx.message
        guild: discord.Guild = ctx.guild
        author: discord.Member = message.author
        ADMIN_CHANNEL = guild.get_channel(ADMIN_CHANNEL_ID)
        await message.delete()

        course_channel: Optional[discord.TextChannel] = None
        try:
            course_channel = await CourseChannelConverter().convert(ctx, name)
        except commands.BadArgument as e:
            if "invalid course format" not in str(e):
                await ADMIN_CHANNEL.send(
                    f"{author.mention} just tried to add `{name}` using the `.choose` command. "
                    "Consider adding this course."
                )
                await ctx.send(
                    f"The course `{name}` is not available but I have notified the admin team to add it.",
                    delete_after=5,
                )
                return

        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        school_or_color: bool = False
        async for message in COURSE_REGISTRATION_CHANNEL.history(
            limit=4, oldest_first=True
        ):
            if (f"({name.upper()})" in message.content) or (
                f"-> {name.title()}" in message.content
            ):
                school_or_color = True
                break
        if school_or_color:
            role: discord.Role = await CaseInsensitiveRoleConverter().convert(ctx, name)
            if role in author.roles:
                await author.remove_roles(role)
                await ctx.send(f"`{role.name}` has been removed.", delete_after=5)
            else:
                await author.add_roles(role)
                await ctx.send(f"`{role.name}` has been added!", delete_after=5)
        elif course_channel:
            overwrites: discord.PermissionOverwrite = course_channel.overwrites_for(
                author
            )
            if overwrites.is_empty():
                await course_channel.set_permissions(
                    author, read_messages=True, send_messages=True
                )
                await ctx.send(
                    f"You have enrolled in `{course_channel.topic}`", delete_after=5
                )
            else:
                await course_channel.set_permissions(author, overwrite=None)
                await ctx.send(
                    f"You have unenrolled in `{course_channel.topic}`", delete_after=5,
                )
        else:
            await ctx.send(
                f"`{name}` is neither a toggleable role/course.", delete_after=5
            )


def setup(client):
    client.add_cog(CourseSelection(client))
