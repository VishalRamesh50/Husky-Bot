import discord
import json
import re
import string
import urllib.request
from discord.ext import commands

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID


class CreateCourse(commands.Cog):
    """Controls all the operations which must take place to create a new course.
    Will create a new channel and role for it.
    Then will update #course-registration to reflect the changes of the new course.
    Will create a reaction role in #course-registration for people to react and get
    assigned to the course.
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        # max num of reactions allowed per message
        self.REACTION_LIMIT: int = 20

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["newCourse"])
    async def new_course(
        self, ctx: commands.Context, name: str, *channel_name_parts
    ) -> None:
        """Creates a new course channel and role if one does not already exist.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        name: `str`
            The course acronym and the role name.
        channel_name_parts: `Tuple`
            The name of the channel in a tuple.
        """

        if not channel_name_parts:
            await ctx.send("No channel name was given")
            return

        name = name.upper()
        pattern = re.compile(r"^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$")
        if not pattern.match(name):
            await ctx.send(
                "Not a valid course pattern: `ABCD-1234`/`AB-1234`/`ABCD-12XX`/`AB-12XX`"
            )
            return

        guild: discord.Guild = ctx.guild
        if any(name == r.name for r in guild.roles):
            await ctx.send(
                f"The role: `{name}` already exists. "
                "Are you sure this course doesn't already exist?"
            )
            return

        with ctx.channel.typing():
            role: discord.Role = await guild.create_role(
                name=name, reason="Creating a new course"
            )

            course_category: str = name.split("-")[0]
            course_num: int = int(re.sub(r"\D", "0", name.split("-")[1]))
            role_position: int = 0
            for r in reversed(sorted(await guild.fetch_roles())):
                if r.name.split("-")[0] == course_category and r != role:
                    curr_course_num: int = int(re.sub(r"\D", "0", r.name.split("-")[1]))
                    role_position = r.position
                    if course_num > curr_course_num:
                        role_position = r.position + 1
                        break

            await role.edit(position=role_position)
            await ctx.send(f"A new role named `{role.name}` was created")

        # TODO: Work on channel creation and category
        channelName = ' '.join(channelName)
        NEW_COURSE_ROLE = discord.utils.get(guild.roles, name=name)
        channel_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            NEW_COURSE_ROLE: discord.PermissionOverwrite(read_messages=True)
        }
        category = discord.utils.get(guild.categories, name=courseCategory)

        # if the category already exists
        if category:
            # create the new course channel
            channel = await category.create_text_channel(channelName, overwrites=channel_overwrites)
            # if there were more 0 channels before adding the new channel
            if len(category.channels) > 1:
                # get the position of the last channel before adding the new channel
                position = category.channels[-2].position + 1
            else:
                # default the position to the new channel's position
                position = channel.position
            for c in category.channels:
                # find the role object from the list of roles in the channel perms by looking for a '-' in the name
                role = next((r for r in list(c.overwrites.keys()) if '-' in r.name), None)
                # if the correct role object is found
                if role:
                    # replace any characters with 0s
                    currCourseNum = int(re.sub(r'\D', '0', role.name.split('-')[1]))
                    # if the new course's number is less than current course's num
                    if courseNum < currCourseNum:
                        # if there is no gap
                        if (discord.utils.get(guild.channels, position=c.position - 1)):
                            position = c.position
                        # if there is a gap
                        else:
                            position = c.position - 1
                        break
            # adjust the position of the channel to the appropriate position according to course number
            await channel.edit(position=position)
            await ctx.send(f"A channel named `{channel.name}` was created in the `{category.name}` category")
            return True
        # if the category does not already exist
        else:
            NOT_REGISTERED_ROLE = discord.utils.get(guild.roles, name="Not Registered")
            category_overwrites = {
                guild.default_role: discord.PermissionOverwrite(mention_everyone=True),
                NOT_REGISTERED_ROLE: discord.PermissionOverwrite(read_messages=False)
            }
            # create a new category if it doesn't exist
            category = await guild.create_category_channel(courseCategory, overwrites=category_overwrites)
            await ctx.send(f"A new category `{courseCategory}` was created")
            # create the new channel
            channel = await guild.create_text_channel(name=channelName, category=category, overwrites=channel_overwrites)
            await ctx.send(f"A channel named `{channel.name}` was created in the `{category.name}` category")
            return True

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newCourseReaction(self, ctx, courseRole: discord.Role, *courseDescription):
        guild = ctx.guild
        COURSE_REGISTRATION_CHANNEL = guild.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        pattern = re.compile(r'^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$')
        # if name does not follow a course format
        if not pattern.match(courseRole.name):
            await ctx.send("Not a valid course pattern: `ABCD-1234`/`AB-1234`/`ABCD-12XX`/`AB-12XX`")
            return

        courseCategory = courseRole.name.split('-')[0]
        courseNum = int(re.sub(r'\D', '0', courseRole.name.split('-')[1]))
        courseDescription = ' '.join(courseDescription)
        courseRegistrationMessages = await COURSE_REGISTRATION_CHANNEL.history(limit=None).flatten()
        # go through each message in #course-registration
        for message_index, message in enumerate(courseRegistrationMessages):
            # if an embedded message exists, message is now the reaction role message
            if (message.embeds):
                embed = message.embeds[0]
                # if the given role's course category matches the message's
                if f"Add/Remove {courseCategory} courses" == embed.title:
                    # the description message descibing which emojis to react to for each courses
                    descriptionMessage = courseRegistrationMessages[message_index - 1]
                    try:
                        alpha_index: int = len(message.reactions)
                        # no need to check for 2 msg above due to format of #course-registration
                        upper_message: discord.Message = courseRegistrationMessages[message_index + 2]
                        if upper_message.embeds:
                            second_embed = upper_message.embeds[0]
                            if f"Add/Remove {courseCategory} courses" == second_embed.title:
                                # if there is still space for reactions
                                if len(upper_message.reactions) < self.REACTION_LIMIT:
                                    # assign the reaction roles to modify the upper messages
                                    descriptionMessage = courseRegistrationMessages[message_index + 1]
                                    message = upper_message
                                    alpha_index = len(message.reactions)
                                else:
                                    # create an offset for the letters
                                    alpha_index = len(message.reactions) + len(upper_message.reactions)
                        # set the new emoji letter to the next letter in the alphabet
                        emoji_letter = string.ascii_lowercase[alpha_index]
                    # if there are 26 or more reactions already and A-Z have been exhausted
                    except IndexError:
                        await ctx.send("There are too many reactions already")
                        return
                    emoji_name = f"regional_indicator_{emoji_letter}"
                    # load json of valid unicode emojis
                    emojiJson = "https://gist.githubusercontent.com/Vexs/629488c4bb4126ad2a9909309ed6bd71/raw/da8c23f4a42f3ad7cf829398b89bda5347907fef/emoji_map.json"
                    with urllib.request.urlopen(emojiJson) as url:
                        data = json.loads(url.read().decode())
                    emoji = data[emoji_name]

                    content = descriptionMessage.content
                    # if the course number already exists in the description message (aka reaction role exists)
                    if str(courseNum) in content:
                        await ctx.send(f"The given course already has a reaction role setup in {COURSE_REGISTRATION_CHANNEL.mention}")
                        return
                    content = content.split('\n')
                    # add the current course to the end as a default position
                    content.append(f"{emoji} -> {courseDescription} ({courseCategory} {courseNum})")
                    # go through each line in the content (each course)
                    for index, course_item in enumerate(content):
                        # gets the course number from the end of the course description
                        currCourseNum = int(re.sub(r'\D', '0', course_item[-5:-1]))
                        # if this is a new course stub
                        if (currCourseNum == 0):
                            del content[index]
                            break
                        else:
                            if courseNum < currCourseNum:
                                # remove the course from the last position and put it in the correct position
                                del content[-1]
                                # insert new course at the appropriate location
                                content.insert(index, f"{emoji} -> {courseDescription} ({courseCategory} {courseNum})")
                                break
                    content = '\n'.join(content)
                    # edit the course description message with the new course inserted
                    await descriptionMessage.edit(content=content)
                    # create a reaction role for the embeded message
                    await ctx.invoke(self.newrr, *[COURSE_REGISTRATION_CHANNEL.mention, message.id, emoji, courseRole.mention])
                    return
        await ctx.send(f"No embedded message was found for the category `{courseCategory}`")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newCourseComplete(self, ctx, courseRoleName, *args):
        args = ' '.join(args)
        # if the comma separator was not used
        if ',' not in args:
            await ctx.send("Split the channel name and course description with a comma")
            return
        args = args.split(',')
        channelDescription = args[0]
        courseDescription = args[1]
        # if either of the descriptions are empty
        if channelDescription.strip() == "" or courseDescription.strip() == "":
            await ctx.send("Your channel & course description must have content")
            return
        # if the course command succesfully executed with no user errors
        # create the new course role and channel
        if(await ctx.invoke(self.newCourse, courseRoleName, *[channelDescription])):
            role = discord.utils.get(ctx.guild.roles, name=courseRoleName.upper())
            # create the new reaction role and update the course descriptions
            await ctx.invoke(self.newCourseReaction, role, *[courseDescription])


def setup(client: commands.Bot):
    client.add_cog(CreateCourse(client))
