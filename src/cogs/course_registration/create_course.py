import discord
import re
import requests
import string
from discord.ext import commands
from typing import List, Optional

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID
from .regex_patterns import IS_COURSE_ACRONYM


class CreateCourse(commands.Cog):
    """Controls all the operations which must take place to create a new course.
    Will create a new channel for it.
    Then will update #course-registration to reflect the changes of the new course.
    Will create a reaction channel in #course-registration for people to react and get
    assigned to the course.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["newCourse"])
    async def new_course(
        self, ctx: commands.Context, name: str, *, channel_name: str
    ) -> bool:
        """Creates a new course channel and role if one does not already exist.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        name: `str`
            The course acronym and the role name.
        channel_name: `str`
            The name of the channel.

        Returns
        -----------
        True if both the channel and role were created succesfully, else False.
        """
        name = name.upper()
        if not IS_COURSE_ACRONYM.match(name):
            await ctx.send(
                "Not a valid course pattern: `ABCD-1234`/`AB-1234`/`ABCD-12XX`/`AB-12XX`"
            )
            return False

        course_category: str = name.split("-")[0]
        course_num: int = int(re.sub(r"\D", "0", name.split("-")[1]))
        guild: discord.Guild = ctx.guild
        with ctx.channel.typing():
            channel_overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
            }
            category: discord.CategoryChannel = discord.utils.get(
                guild.categories, name=course_category
            )
            # create a new category for the course if it doesn't already exist
            if category is None:
                category = await guild.create_category(
                    course_category,
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            read_messages=False, mention_everyone=True
                        )
                    },
                    reason="New course",
                )
                await ctx.send(f"A new category `{category.name}` was created.")

            # create and insert the channel in order
            channel: discord.TextChannel = await category.create_text_channel(
                channel_name, overwrites=channel_overwrites, reason="New course"
            )
            await channel.edit(topic=f"{name} (0 enrolled)")
            if len(category.channels) > 1:
                for c in category.channels:
                    course_name = c.topic
                    # sometimes the newly created channel's topic is None so ignore it
                    if course_name:
                        curr_course_num = int(
                            re.sub(r"\D", "0", course_name.split("-")[1][:4])
                        )
                        channel_position: int = c.position
                        if course_num > curr_course_num:
                            await channel.edit(position=channel_position)
                            break
            await ctx.send(
                f"A channel named `{channel_name}` was created in the `{category.name}` category."
            )
            return True

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["newCourseReaction"])
    async def new_course_reaction(
        self, ctx: commands.Context, course_abbr: str, *, course_name: str
    ) -> bool:
        """Creates a reaction role for the course.
        Will also edit the message for course description lists under the embedded message.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        course_abbr: `str`
            The course abbreviation as category acronym and course number divided with a dash.
        course_name:  `str`
            The name of the course to be added in the course reaction role description.

        Returns
        -----------
        True if the reaction role for the course was created successfully, else False.
        """
        guild: discord.Guild = ctx.guild
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        if not IS_COURSE_ACRONYM.match(course_abbr):
            await ctx.send(
                "Not a valid course pattern: `ABCD-1234`/`AB-1234`/`ABCD-12XX`/`AB-12XX`"
            )
            return False

        course_category: str = course_abbr.split("-")[0]
        course_num: int = int(re.sub(r"\D", "0", course_abbr.split("-")[1]))
        course_registration_messages: List[
            discord.Message
        ] = await COURSE_REGISTRATION_CHANNEL.history(
            limit=None, oldest_first=True
        ).flatten()
        alpha_index: int = 0
        reaction_role_message: Optional[discord.Message] = None
        for index, message in enumerate(course_registration_messages):
            if message.embeds:
                embed: discord.Embed = message.embeds[0]
                if f"Add/Remove {course_category} courses" == embed.title:
                    reaction_role_message = message
                    description_message: discord.Message = course_registration_messages[
                        index + 1
                    ]
                    content: str = description_message.content
                    if str(course_num) in content:
                        await ctx.send(
                            f"The given course already has a reaction role setup in {COURSE_REGISTRATION_CHANNEL.mention}"
                        )
                        return False

                    num_reactions: int = len(message.reactions)
                    alpha_index += num_reactions
                    try:
                        emoji_letter: str = string.ascii_lowercase[alpha_index]
                    except IndexError:
                        await ctx.send("A-Z has already been used for reactions.")
                        return False
                    EMOJI_JSON_URL = "https://gist.githubusercontent.com/Vexs/629488c4bb4126ad2a9909309ed6bd71/raw/da8c23f4a42f3ad7cf829398b89bda5347907fef/emoji_map.json"
                    emoji: str = requests.get(EMOJI_JSON_URL).json()[
                        f"regional_indicator_{emoji_letter}"
                    ]
                    # check to see if this message has reached it's reaction limit
                    # if so continue to search for another message, otherwise break
                    # now and add a reaction role here
                    try:
                        await message.add_reaction(emoji)
                        await message.remove_reaction(emoji, self.client.user)
                        break
                    except discord.Forbidden:
                        pass

        if reaction_role_message is None:
            await ctx.send(
                f"No embedded message was found for the category `{course_category}`"
            )
            return False

        split_content: List[str] = content.split("\n")
        description: str = f"{emoji} -> {course_name} ({course_category} {course_num})"
        split_content.append(description)
        for index, course_item in enumerate(split_content):
            curr_course_num: int = int(re.sub(r"\D", "0", course_item[-5:-1]))
            if curr_course_num == 0:
                split_content = [description]
                break
            elif course_num < curr_course_num:
                del split_content[-1]
                split_content.insert(index, description)
                break
        content = "\n".join(split_content)
        await description_message.edit(content=content)
        category: discord.CategoryChannel = discord.utils.get(
            guild.categories, name=course_category
        )
        reaction_role_command: commands.Command = self.client.get_command("newrc")
        for c in category.text_channels:
            if c.topic and c.topic.startswith(course_abbr):
                await ctx.invoke(
                    reaction_role_command,
                    *[COURSE_REGISTRATION_CHANNEL, message.id, emoji, c],
                )
                return True
        return False

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["newCourseComplete"])
    async def new_course_complete(
        self, ctx: commands.Context, course_role_name: str, *, descriptions: str
    ) -> None:
        """Creates a role, channel, and reaction role for the course.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        course_role_name: `str`
            The name of the role associated with the course.
        description: `str`
            A comma separated string containing the channel name in the first half
            and the course description in the second.
        """
        if "," not in descriptions:
            await ctx.send("Split the channel name and course description with a comma")
            return
        channel_name = descriptions.split(",")[0].strip()
        course_name = descriptions.split(",")[1].strip()

        if channel_name == "" or course_name == "":
            await ctx.send("Your channel & course description must have content")
            return

        if await self.new_course(ctx, course_role_name, channel_name=channel_name):
            await self.new_course_reaction(
                ctx, course_role_name, course_name=course_name
            )


def setup(client: commands.Bot):
    client.add_cog(CreateCourse(client))
