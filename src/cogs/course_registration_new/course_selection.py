import discord
from discord.ext import commands
from typing import Optional

from checks import is_admin, in_channel
from converters import CaseInsensitiveRoleConverter, CourseChannelConverter
from data.ids import COURSE_REGISTRATION_CHANNEL_ID, ADMIN_CHANNEL_ID


class CourseSelectionChannel(commands.Cog):
    """Handles the interaction surrounding selecting courses or other roles
    from course-regisration via commands and clean-up.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    @commands.guild_only()
    @commands.check_any(in_channel(COURSE_REGISTRATION_CHANNEL_ID), is_admin())
    async def choose_channel(self, ctx: commands.Context, *, name: str) -> None:
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
                    f"You have enrolled in the `{course_channel.topic}`", delete_after=5
                )
            else:
                await course_channel.set_permissions(author, overwrite=None)
                await ctx.send(
                    f"You have unenrolled in the `{course_channel.topic}`",
                    delete_after=5,
                )
        else:
            await ctx.send(
                f"`{name}` is neither a toggleable role/course.", delete_after=5
            )


def setup(client):
    client.add_cog(CourseSelectionChannel(client))
