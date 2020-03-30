import asyncio
import discord
import json
import re
import string
import urllib.request
from discord.ext import commands
from typing import List, Dict

from checks import is_admin, in_channel
from data.ids import COURSE_REGISTRATION_CHANNEL_ID, ADMIN_CHANNEL_ID


class CourseRegistration(commands.Cog):
    def __init__(self, client):
        self.client = client
        # flag to determine whether all non-admin messages should be deleted or not on send
        self.deleteMessages = True
        # max num of reactions allowed per message
        self.REACTION_LIMIT: int = 20

    # returns a lower-case string without dashes and stripping whitespace
    def ignoreDashCase(self, input):
        return ' '.join(input.split('-')).lower().strip()

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        channel = message.channel
        # if message not a webhook & user has an administrator permissions
        admin = message.webhook_id is None and author.permissions_in(channel).administrator
        # AutoDelete Non-Admin Messages in #course-registration if flag is set
        if channel.id == COURSE_REGISTRATION_CHANNEL_ID:
            # if user is not an admin or HuskyBot
            if (not admin and author != self.client.user):
                await asyncio.sleep(5)
                await message.delete()
            else:
                # if flag is set to True and the user is HuskyBot
                if self.deleteMessages and author == self.client.user:
                    await asyncio.sleep(5)
                    await message.delete()

    # toggles #course-registration auto-deletion
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def toggleAD(self, ctx):
        self.deleteMessages = not self.deleteMessages
        await ctx.send(f"Auto-deletion was toggled to: {self.deleteMessages}")

    # toggles course registration roles
    @commands.command()
    @commands.check_any(in_channel(COURSE_REGISTRATION_CHANNEL_ID), is_admin())
    async def choose(self, ctx, *args):
        message = ctx.message
        guild = ctx.guild
        member = message.author
        ADMIN_CHANNEL = self.client.get_channel(ADMIN_CHANNEL_ID)
        admin = member.permissions_in(ctx.channel).administrator
        args = ' '.join(args).strip()
        role = None
        await message.delete()  # deletes command
        # tries to find a role given the user input
        try:
            role = await commands.RoleConverter().convert(ctx, args)
        # if a role could not be found
        except discord.ext.commands.errors.BadArgument as e:
            for r in guild.roles:
                # if the given input is the same as a role when lowercase or/and ignoring dashes
                if (args.lower() == r.name.lower() or
                   self.ignoreDashCase(args) == self.ignoreDashCase(r.name)):
                    role = r
                    break
            # if no role exists
            if role is None:
                await ctx.send(e, delete_after=5)  # sends an error message to user about missing role
                pattern = re.compile(r'^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$')  # regex pattern for courses
                # if the given argument is the format of a course with dashes subbed in for spaces or normally
                if pattern.match(args.upper()) or pattern.match(args.replace(' ', '-').upper()):
                    # notify the admins and tell the user about this notification.
                    await ADMIN_CHANNEL.send(f"{member.mention} just tried to add `{args}` using the `.choose` command. Consider adding this course.")
                    await ctx.send(f"The course `{args}` is not available but I have notified the admin team to add it.", delete_after=5)
                return
        # roles that a normal user is allowed to add other than course roles
        WHITELISTED_COLLEGES = ['CCIS', 'COE', 'BCHS', 'CAMD', 'DMSB', 'COS', 'CSSH', 'NUSL', 'EXPLORE']
        WHITELISTED_COLORS = ['ORANGE', 'LIGHT GREEN', 'YELLOW', 'PURPLE', 'LIGHT BLUE', 'PINK', 'LIGHT PINK', 'PALE PINK', 'CYAN', 'SPRING GREEN', 'PALE YELLOW', 'NAVY BLUE', 'LAVENDER']
        # if the role is one of the whitelisted roles or the user is an admin
        if ('-' in role.name or role.name in WHITELISTED_COLLEGES + WHITELISTED_COLORS or admin):
            # try to add or a remove a role to/from a user
            try:
                # if the role is already one of the user's role
                if (role in member.roles):
                    # remove the role from the user
                    await member.remove_roles(role)
                    await ctx.send(f"`{role.name}` has been removed.", delete_after=5)
                else:
                    # add the role to the user
                    await member.add_roles(role)
                    await ctx.send(f"`{role.name}` has been added!", delete_after=5)
            # in case of insufficient bot permissions
            except discord.errors.Forbidden:
                await ctx.send("I do not have permission to alter that role", delete_after=5)
        # if the role is not one of the whitelisted courses members are allowed to add.
        else:
            await ctx.send("You do not have the permission to toggle that role 🙃", delete_after=5)

    # removes all course roles from every member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newSemester(self, ctx):
        # remove course roles from every member
        async with ctx.channel.typing():
            await ctx.send("Goodbye courses...")
            for member in ctx.guild.members:
                rolesToRemove = list(filter(lambda r: '-' in r.name, member.roles))
                await member.remove_roles(*rolesToRemove, atomic=False)
            await ctx.send("Removed everyone's classes! WOO!")

        # reset reaction roles from every course message
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        async with COURSE_REGISTRATION_CHANNEL.typing():
            await ctx.send(f"Starting to clear up {COURSE_REGISTRATION_CHANNEL.mention}...")
            async for message in COURSE_REGISTRATION_CHANNEL.history(limit=None):
                if message.embeds and 'Add/Remove' in message.embeds[0].title:
                    reaction_cog: commands.Cog = self.client.get_cog('Reaction')
                    # remove all the reaction roles from the message
                    await reaction_cog.removeallrr.callback(reaction_cog, ctx, message.id)
                    # remove all the reactions from the message
                    await message.clear_reactions()
            await ctx.send(f"Finished reseting all reaction roles in {COURSE_REGISTRATION_CHANNEL.mention}!")

    # removes all course roles from every member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearCourses(self, ctx, member: discord.Member):
        await ctx.send(f"Clearing course roles for {member.name}...")
        rolesToRemove = list(filter(lambda r: '-' in r.name, member.roles))
        await member.remove_roles(*rolesToRemove, atomic=False)
        await ctx.send(f"Done removing all roles for {member.name}!")

    # removes all reactions from the given member in the course registration channel
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearReactions(self, ctx, member: discord.Member):
        COURSE_REGISTRATION_CHANNEL = self.client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        await ctx.send(f"Clearing reactions for {member.name} in {COURSE_REGISTRATION_CHANNEL.mention}...")
        async for message in COURSE_REGISTRATION_CHANNEL.history(limit=None):
            for reaction in message.reactions:
                await reaction.remove(member)
        await ctx.send(f"Done removing all reactions for {member.name}!")

    # sends a new embedded msg with the given title and image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newEmbed(self, ctx, *args):
        await ctx.message.delete()
        args = ' '.join(args)
        if ',' not in args:
            await ctx.send("Use a comma to separate the title and image url")
            return
        args = args.split(',')
        title = args[0].strip()
        url = args[1].strip()
        if title == "" or url == "":
            await ctx.send("Title and url must have content")
            return
        embed = discord.Embed(
            title=title,
            colour=discord.Color.from_rgb(52, 54, 59)
        )
        try:
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            await ctx.send(":regional_indicator_a: -> Course Description (SampleCourse XXXX)")
        except discord.errors.HTTPException:
            await ctx.send(f"Not a valid image url")

    # edits the images for all the embedded messages in the given msg to the given image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editEmbedImage(self, ctx, message: discord.Message, url):
        await ctx.message.delete()
        for embed in message.embeds:
            try:
                embed.set_image(url=url)
                await message.edit(embed=embed)
                await ctx.send(f"Image for `{embed.title}` was edited")
            except discord.errors.HTTPException:
                await ctx.send("Not a valid image url")

    # edits the title for all the embedded messages in the given msg to the given title
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editEmbedTitle(self, ctx, message: discord.Message, *args):
        await ctx.message.delete()
        title = ' '.join(args)
        for embed in message.embeds:
            embed.title = title
            await message.edit(embed=embed)
            await ctx.send(f"Title for message `{message.id}` was edited")

    # edits the content of the message use '\n' to indicate newline
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editCourseContent(self, ctx, message: discord.Message, *args):
        await ctx.message.delete()
        if message.embeds == []:
            args = ' '.join(args).split("\\n")
            content = []
            for arg in args:
                content.append(arg.strip())
            content = '\n'.join(content)
            await message.edit(content=content)
            await ctx.send(f"Content for message `{message.id}` was edited")
        else:
            await ctx.send("You accidentally tried to edit the embedded message", delete_after=5)

    # sends a new embedded msg with the given title and image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def navEmbed(self, ctx):
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        # get all the messages in course-registration
        messages: List[discord.Message] = await COURSE_REGISTRATION_CHANNEL.history(limit=None).flatten()
        # filter out all the messages which don't have embeds or a title
        messages = list(filter(lambda x: x.embeds and x.embeds[0].title, messages))
        # sort the messages by their embed's title
        messages.sort(key=lambda m: (m.embeds[0].title))
        letter_to_link: Dict[str, str] = {}
        # assign a letter to the first jump_link of a message
        for message in messages:
            course: str = message.embeds[0].title.replace('Add/Remove ', '')
            starting_letter: str = course[0]
            # if the course starting with the letter has not been added yet
            if letter_to_link.get(starting_letter) is None:
                letter_to_link[starting_letter] = message.jump_url

        alpha_links: str = ""
        # Each letter has it's own thing
        for letter, link in letter_to_link.items():
            alpha_links += f"[{letter}]({link}) **|** "

        # remove the trailing divider
        alpha_links = alpha_links[:-7]
        try:
            embed = discord.Embed(
                title="Quick Links!",
                description=f"Jump to each course category starting with the given letter by simply clicking on the links below\n{alpha_links}",
                colour=discord.Colour.red()
            )
        # if there are too many characters in the description
        except 400 as e:
            print(type(e))
            print(e)
            embed = discord.Embed(
                title="Quick Links!",
                description=f"Jump to each course category starting with the given letter by simply clicking on the links below",
                colour=discord.Colour.red()
            )
            # Divide by the middle for 2 groups
            # 7 links is about the most a field can hold
            middle: int = min(len(letter_to_link) // 2, 7)
            counter: int = 0
            for key, val in letter_to_link.items():
                alpha_links += f"[{key}]({val}) "
                counter += 1
                if counter % middle == 0 or counter == len(letter_to_link):
                    embed.add_field(name=f"{alpha_links[1]}-{key}", value=alpha_links, inline=True)

        top_messages: List[discord.Message] = await COURSE_REGISTRATION_CHANNEL.history(limit=4, oldest_first=True).flatten()
        embed.add_field(name=f"Top Of Page", value=f"[Pick School/Major Here]({top_messages[0].jump_url})", inline=True)
        embed.add_field(name=f"Colors", value=f"[Choose Colors Here]({top_messages[2].jump_url})", inline=True)
        await ctx.send(embed=embed)

    # removes all reaction roles from the given message
    # returns True when succesfully executed with no user errors else False
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newCourse(self, ctx, name, *channelName):
        name = name.upper()
        pattern = re.compile(r'^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$')
        # if name does not follow a course format
        if not pattern.match(name):
            await ctx.send("Not a valid course pattern: `ABCD-1234`/`AB-1234`/`ABCD-12XX`/`AB-12XX`")
            return False
        # if a channel name was not given
        if not channelName:
            await ctx.send("No channel name was given")
            return False
        guild = ctx.guild
        # if the role already exists
        if name in [r.name for r in guild.roles]:
            await ctx.send('This role already exists')
            return False

        # create the new course role if it doesn't exist
        role = await guild.create_role(name=name, mentionable=True)
        courseCategory = name.split('-')[0]
        courseNum = int(re.sub(r'\D', '0', name.split('-')[1]))
        rolePosition = 1
        for r in guild.roles:
            if r.name.split('-')[0] == courseCategory:
                # if there is no gap above
                if (discord.utils.get(guild.roles, position=r.position + 1)):
                    rolePosition = r.position
                # if there is a gap above
                else:
                    rolePosition = r.position + 1
                # replace any characters with 0s
                currCourseNum = int(re.sub(r'\D', '0', r.name.split('-')[1]))
                if courseNum < currCourseNum:
                    rolePosition = r.position - 1
                    break
        await role.edit(position=rolePosition)
        await ctx.send(f"A new role named `{role.name}` was created")

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


def setup(client):
    client.add_cog(CourseRegistration(client))
