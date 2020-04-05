import discord
import re
from discord.ext import commands

from checks import is_admin, in_channel
from converters import CourseRoleConverter
from data.ids import COURSE_REGISTRATION_CHANNEL_ID, ADMIN_CHANNEL_ID


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
    @commands.command()
    async def toggleAD(self, ctx: commands.Context) -> None:
        """Toggles the delete_self_message flag."""
        self.delete_self_message = not self.delete_self_message
        await ctx.send(
            f"Deleting self-messages was toggled to: {self.delete_self_message}"
        )

    @commands.command()
    @commands.guild_only()
    @commands.check_any(in_channel(COURSE_REGISTRATION_CHANNEL_ID), is_admin())
    async def choose(self, ctx: commands.Context, *role_name_parts) -> None:
        """Command to add or remove any roles from the person invoking the command.
        If the author is not an admin, they can only toggle roles which are available
        in the course-registration channel.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        role_name_parts: `Tuple`
            The role name to be toggled as a tuple of strings.
        """
        message: discord.Message = ctx.message
        guild: discord.Guild = ctx.guild
        author: discord.Member = message.author
        ADMIN_CHANNEL = guild.get_channel(ADMIN_CHANNEL_ID)
        admin: bool = author.permissions_in(ctx.channel).administrator
        role_name: str = " ".join(role_name_parts)
        await message.delete()

        try:
            role: discord.Role = await CourseRoleConverter().convert(ctx, role_name)
        except commands.BadArgument as e:
            await ctx.send(e, delete_after=5)
            pattern = re.compile(r"^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$")
            # if the role seems to follow a valid course format
            if pattern.match(role_name.upper()) or pattern.match(
                role_name.replace(" ", "-").upper()
            ):
                await ADMIN_CHANNEL.send(
                    f"{author.mention} just tried to add `{role_name}` using the `.choose` command. "
                    "Consider adding this course."
                )
                await ctx.send(
                    f"The course `{role_name}` is not available but I have notified the admin team to add it.",
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
            if (f"({role.name})" in message.content) or (
                f"-> {role.name.title()}" in message.content
            ):
                school_or_color = True
                break
        if "-" in role.name or school_or_color or admin:
            try:
                if role in author.roles:
                    await author.remove_roles(role)
                    await ctx.send(f"`{role.name}` has been removed.", delete_after=5)
                else:
                    await author.add_roles(role)
                    await ctx.send(f"`{role.name}` has been added!", delete_after=5)
            except discord.errors.Forbidden:
                await ctx.send(
                    "I do not have permission to alter that role", delete_after=5
                )
        else:
            await ctx.send(
                "You do not have the permission to toggle that role 🙃", delete_after=5
            )


def setup(client):
    client.add_cog(CourseSelection(client))
