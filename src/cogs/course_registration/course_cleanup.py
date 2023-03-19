import asyncio
import discord
import string
from discord.ext import commands
from typing import List, Tuple

from checks import is_admin
from client.bot import Bot
from data.ids import COURSE_REGISTRATION_CHANNEL_ID
from regex_patterns import IS_COURSE


class CourseCleanup(commands.Cog):
    """Has some commands to handle mass removals of channel access
    and/or reactions related to course registration.
    """

    def __init__(self, client: Bot):
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
        messages = [
            message
            async for message in COURSE_REGISTRATION_CHANNEL.history(
                limit=None, oldest_first=True
            )
        ]
        for index, message in enumerate(messages):
            if message.embeds and "Add/Remove" in str(message.embeds[0].title):
                newrc_command: commands.Command = self.client.get_command("newrc")
                for course_line in messages[index + 1].content.split("\n"):
                    reaction, course_name = course_line.split(" -> ")
                    reaction_unicode: str = self.client.emoji_map.get(
                        reaction[1:-1], reaction
                    )
                    start_index: int = course_name.find("(") + 1
                    end_index: int = course_name.find(")")
                    course_acronym: str = course_name[start_index:end_index].replace(
                        " ", "-"
                    )
                    target_channel: discord.TextChannel = discord.utils.find(
                        lambda c: c.topic and course_acronym in c.topic,
                        guild.text_channels,
                    )
                    if target_channel:
                        await ctx.invoke(
                            newrc_command,
                            COURSE_REGISTRATION_CHANNEL,
                            message.id,
                            reaction_unicode,
                            target_channel,
                        )
        await ctx.send("All reaction channels were added back for courses!")

    @is_admin()
    @commands.guild_only()
    @commands.command()
    async def clone_cr(self, ctx: commands.Context) -> None:
        """Duplicates course embeds and contents in sorted category order and assigning
        emojis in alphabetical order in terms of the course order.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        guild: discord.Guild = ctx.guild
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        messages = [
            message
            async for message in COURSE_REGISTRATION_CHANNEL.history(
                limit=None, oldest_first=True
            )
        ]
        category_messages: List[Tuple[str, discord.Embed, discord.Message]] = []
        for index, message in enumerate(messages):
            if message.embeds:
                embed_msg: discord.Embed = message.embeds[0]
                embed_title: str = str(embed_msg.title)
                if "Add/Remove" in embed_title:
                    category_name: str = embed_title.split()[1]
                    category_messages.append(
                        (category_name, embed_msg, messages[index + 1])
                    )

        category_messages.sort(key=lambda m: m[0])
        for category_name, embed, msg in category_messages:
            new_embed_cmd: commands.Command = self.client.get_command("new_embed")
            await ctx.invoke(
                new_embed_cmd,
                embed.image.url,
                title=f"Add/Remove {category_name} courses",
            )
            lines: List[str] = msg.content.split("\n")
            for index, line in enumerate(lines):
                course_desc: str = line.split(" -> ")[-1]
                lines[
                    index
                ] = f":regional_indicator_{string.ascii_lowercase[index]}: -> {course_desc}"

            content: str = "\n".join(lines)
            await ctx.send(content)
            # quick and dirty way to ensure to some degree that embeds are created in order
            await asyncio.sleep(5)

        await ctx.send("Cloning complete!")

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


async def setup(client):
    await client.add_cog(CourseCleanup(client))
