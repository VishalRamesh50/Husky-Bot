import discord
import json
import os
import pymongo
import random
import re
import string
import urllib.request
from discord.ext import commands
from pymongo.collection import Collection
from typing import Optional

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID

DB_CONNECTION_URL = os.environ["DB_CONNECTION_URL"]
mongoClient = pymongo.MongoClient(DB_CONNECTION_URL)
reactive_roles: Collection = mongoClient.reactions.reactive_roles


class Reaction(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        # max num of reactions allowed per message
        self.REACTION_LIMIT: int = 20

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        """Adds the role associated with a reaction role if one exists
        when a member adds a reaction to a message.

        Parameters
        -------------
        payload: `discord.RawReactionActionEvent`
            The reaction payload with information about the event.
        """

        member: Optional[discord.Member] = payload.member
        if not (payload.guild_id and member) or member.bot:
            return

        guild: discord.Guild = self.client.get_guild(payload.guild_id)

        specs = {
            "server_id": guild.id,
            "message_id": payload.message_id,
            "reaction": payload.emoji.name,
        }
        result: Optional[dict] = reactive_roles.find_one(specs)
        if result:
            role_object: discord.Role = guild.get_role(result["role_id"])
            await member.add_roles(role_object)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        """Removes the role associated with a reaction role if one exists
        when a member removes a reaction from a message.

        Parameters
        ------------
        payload: `discord.RawReactionActionEvent`
            The reaction payload with information about the event.
        """

        if payload.guild_id is None:
            return
        guild: discord.Guild = self.client.get_guild(payload.guild_id)
        member: Optional[discord.Member] = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        specs = {
            "server_id": guild.id,
            "message_id": payload.message_id,
            "reaction": payload.emoji.name,
        }
        result: Optional[dict] = reactive_roles.find_one(specs)
        if result:
            role_object: discord.Role = guild.get_role(result["role_id"])
            await member.remove_roles(role_object)

    @is_admin()
    @commands.command()
    async def newrr(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        message_id: int,
        reaction: str,
        role: discord.Role,
    ) -> None:
        """Creates a new reaction role if one does not already exist.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        channel: `discord.TextChannel`
            The channel which to add the reaction role in.
        message_id: `int`
            The message id of the message to add a reaction role to.
        reaction: `discord.Emoji`
            The emoji which the reaction role will be associated with.
        role: `discord.Role`
            The role which the reaction role will be associated with.
        """

        alphabet: str = string.ascii_letters + string.digits + "-_"
        while True:
            key: str = "".join(random.choice(alphabet) for i in range(9))
            if not reactive_roles.find_one({"key": key}):
                break

        try:
            message: discord.Message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Given message could not be retreived")
            return

        try:
            await message.add_reaction(reaction)
        except discord.Forbidden:
            await ctx.send("This message already has the maximum number of reactions.")
            return
        except (discord.HTTPException, discord.NotFound, discord.InvalidArgument):
            await ctx.send(f'"{reaction}" is not a valid emoij.')
            return

        data = {
            "server_id": ctx.guild.id,
            "message_id": message_id,
            "channel_id": channel.id,
            "reaction": reaction,
            "role_id": role.id,
        }
        if not reactive_roles.find_one(data):
            reactive_roles.insert_one(data)
            reactive_roles.update_one(data, {"$set": {"key": key}})
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(
                name="New Reaction Role Set!", icon_url=self.client.user.avatar_url
            )
            embed.set_thumbnail(url=self.client.user.avatar_url)
            embed.add_field(name="🔑 Key", value=key, inline=False)
            embed.add_field(name="📺 Channel", value=channel.mention, inline=False)
            embed.add_field(name="💬 Message", value=message_id, inline=False)
            embed.add_field(name="🎨 Reaction", value=reaction, inline=False)
            embed.add_field(name="🏷 Role", value=role.mention, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("This reaction role already exists.")

    @newrr.error
    async def newrr_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Error handler for newrr command.
        If valid argument were not given, send feedback to user.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        error `commands.CommandError`:
            The error which was raised.
        """

        if isinstance(error, commands.BadArgument):
            if isinstance(error.__cause__, ValueError):
                await ctx.send(
                    f"`message_id: {ctx.args.message_id}` is not a valid integer."
                )
            else:
                await ctx.send(error)
            ctx.command_failed = False

    @is_admin()
    @commands.command()
    async def fetchrr(self, ctx: commands.Context, given_message_id: str) -> None:
        """Fetches all the reactions, roles, keys for a given message_id.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        given_message_id: `str`
            A message id as a string.
        """

        guild: discord.Guild = ctx.guild
        try:
            message_id: int = int(given_message_id)
        except ValueError:
            await ctx.send("The given message_id must be an integer.")
            return

        options = {"server_id": guild.id, "message_id": message_id}
        if reactive_roles.count_documents(options, limit=1):
            await ctx.send(f"There are no reaction roles set for message: {message_id}")
        else:
            embed = embed = discord.Embed(
                description=(f"Message ID: `{message_id}`"), colour=discord.Colour.red()
            )
            embed.set_author(
                name="Keys and Reactions!", icon_url=self.client.user.avatar_url
            )
            for doc in reactive_roles.find(options):
                key: str = doc["key"]
                reaction: str = doc["reaction"]
                role: str = guild.get_role(doc["role_id"]).mention
                embed.add_field(name=f"`{key}`", value=f"<{reaction}>\n{role}")
            await ctx.send(embed=embed)

    @is_admin()
    @commands.command()
    async def removerr(self, ctx: commands.Context, key: str) -> None:
        """Removes a reaction role from a message tied to the given key.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        key: `str`
            A key to search for a specific reaction role.
        """

        result = reactive_roles.find_one({"key": key})
        if result:
            channel: discord.TextChannel = self.client.get_channel(result["channel_id"])
            message: discord.Message = await channel.fetch_message(result["message_id"])
            await message.remove_reaction(result["reaction"], self.client.user)
            reactive_roles.remove({"key": key})
            await ctx.send(f"Removed reaction role of key `{key}`")
        else:
            await ctx.send("There are no reaction roles with the given key")

    @is_admin()
    @commands.command()
    async def removeallrr(self, ctx: commands.Context, given_message_id: str):
        """Removes all reaction roles from the given message.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        given_message_id: `str`
            A message id as a string.
        """

        try:
            message_id = int(given_message_id)
        except ValueError:
            await ctx.send("The given message_id must be an integer.")
            return

        options = {"server_id": ctx.guild.id, "message_id": message_id}
        if reactive_roles.count_documents(options, limit=1):
            for doc in reactive_roles.find(options):
                channel_object = self.client.get_channel(doc["channel_id"])
                message_object = await channel_object.fetch_message(message_id)
                await message_object.remove_reaction(doc["reaction"], self.client.user)
                reactive_roles.remove({"key": doc["key"]})
            await ctx.send(f"Removed all reaction roles from message: `{message_id}`")
        else:
            await ctx.send("There are no reaction roles for the given message.")

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
    client.add_cog(Reaction(client))
