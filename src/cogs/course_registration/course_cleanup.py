import discord
from discord.ext import commands

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID
from .regex_patterns import IS_COURSE


class CourseCleanup(commands.Cog):
    """Has some commands to handle mass removals of channel access
    and/or reactions related to course registration.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["newSemester"])
    async def new_semester(self, ctx: commands.Context) -> None:
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
                    if c.topic and IS_COURSE.match(c.topic):
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
                    removeallrc_command: commands.Command = self.client.get_command(
                        "removeallrc"
                    )
                    await ctx.invoke(removeallrc_command, message.id)
                    await message.clear_reactions()
            await ctx.send(
                f"Finished reseting all reaction channels in {COURSE_REGISTRATION_CHANNEL.mention}!"
            )

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["autoCourseReactions"])
    async def auto_course_reactions(self, ctx: commands.Context) -> None:
        """Creates course reaction channels for every course in #course-registration
        automatically just by looking at the course content under each course embedded
        message.
        This assumes the format of the course content is like:
        :reaction1: -> Course1 Description (CRSN-1234)\n
        :reaction2: -> Course2 Description (CRSN-4321)

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        guild: discord.Guild = ctx.guild
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        messages = await COURSE_REGISTRATION_CHANNEL.history(
            limit=None, oldest_first=True
        ).flatten()
        for index, message in enumerate(messages):
            if message.embeds and "Add/Remove" in str(message.embeds[0].title):
                newrc_command: commands.Command = self.client.get_command("newrc")
                for course_line in messages[index + 1].content.split("\n"):
                    reaction, course_name = course_line.split(" -> ")
                    start_index: int = course_name.find("(") + 1
                    end_index: int = course_name.find(")")
                    course_acronym: str = course_name[start_index:end_index].replace(
                        " ", "-"
                    )
                    target_channel: discord.TextChannel = discord.utils.find(
                        lambda c: c.topic and course_acronym in c.topic,
                        guild.text_channels,
                    )
                    await ctx.invoke(
                        newrc_command,
                        COURSE_REGISTRATION_CHANNEL,
                        message.id,
                        reaction,
                        target_channel,
                    )
        await ctx.send("All reaction channels were added back for courses!")

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["clearCourses"])
    async def clear_courses(
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
                    if (
                        not c.overwrites_for(member).is_empty()
                        and c.topic
                        and IS_COURSE.match(c.topic)
                    ):
                        await c.set_permissions(member, overwrite=None)
            await ctx.send(f"Done unenrolling {member.name} from all courses!")

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["clearReactions"])
    async def clear_reactions(
        self, ctx: commands.Context, member: discord.Member
    ) -> None:
        """Removes all reactions from the given member in the course registration channel.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        member: `discord.Member`
            The member to remove all reactions from.
        """
        guild: discord.Guild = ctx.guild
        COURSE_REGISTRATION_CHANNEL = guild.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        async with ctx.channel.typing():
            await ctx.send(
                f"Clearing reactions for {member.name} in {COURSE_REGISTRATION_CHANNEL.mention}..."
            )
            async for message in COURSE_REGISTRATION_CHANNEL.history(limit=None):
                for reaction in message.reactions:
                    await reaction.remove(member)
            await ctx.send(f"Done removing all reactions for {member.name}!")


def setup(client):
    client.add_cog(CourseCleanup(client))
