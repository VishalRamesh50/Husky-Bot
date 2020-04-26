import discord
import re
from discord.ext import commands

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID


class CourseCleanupChannel(commands.Cog):
    """Has some commands to handle mass removals of channel access
    and/or reactions related to course registration.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["newSemesterChannel"])
    async def new_semester_channel(self, ctx: commands.Context) -> None:
        """Removes all course roles from every member and removes all reaction roles
        for courses.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        guild: discord.Guild = ctx.guild
        async with ctx.channel.typing():
            await ctx.send("Goodbye courses...")
            for category in guild.categories:
                for c in category.text_channels:
                    pattern = re.compile(r"^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$")
                    if c.topic and pattern.match(c.topic):
                        await c.edit(
                            overwrites={
                                guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False
                                )
                            }
                        )
            await ctx.send("Removed everyone's classes! WOO!")

        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        async with COURSE_REGISTRATION_CHANNEL.typing():
            await ctx.send(
                f"Starting to clear up {COURSE_REGISTRATION_CHANNEL.mention}..."
            )
            async for message in COURSE_REGISTRATION_CHANNEL.history(limit=None):
                if message.embeds and "Add/Remove" in str(message.embeds[0].title):
                    removeallrr_command: commands.Command = self.client.get_command(
                        "removeallrr"
                    )
                    await ctx.invoke(removeallrr_command, message.id)
                    await message.clear_reactions()
            await ctx.send(
                f"Finished reseting all reaction roles in {COURSE_REGISTRATION_CHANNEL.mention}!"
            )

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["clearCoursesChannel"])
    async def clear_courses_channel(
        self, ctx: commands.Context, member: discord.Member
    ) -> None:
        """Unenroll a given member from all courses.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        member: `discord.Member`
            The member to remove all course roles from.
        """
        guild: discord.Guild = ctx.guild
        async with ctx.channel.typing():
            for category in guild.categories:
                for c in category.text_channels:
                    pattern = re.compile(r"^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$")
                    if c.topic and pattern.match(c.topic):
                        await c.set_permissions(member, None)
            await ctx.send(f"Done unenrolling {member.name} from all courses!")


def setup(client):
    client.add_cog(CourseCleanupChannel(client))
