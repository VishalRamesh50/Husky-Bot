import discord
import json
import os
import pymongo
import random
import re
import string
import urllib.request
from discord.ext import commands

from ids import COURSE_REGISTRATION_CHANNEL_ID

DB_CONNECTION_URL = os.environ["DB_CONNECTION_URL"]

# connect to mongodb cluster
mongoClient = pymongo.MongoClient(DB_CONNECTION_URL)
db = mongoClient.reactions  # use the reactions database


class Reaction(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.unique_key = False
        self.valid_channel = False
        self.valid_role = False
        self.valid_message_id = False
        self.valid_emoji = False
        # max num of reactions allowed per message
        self.REACTION_LIMIT = 20

    # inserts data into database if needed, adds reaction to message, displays embeded message with data
    async def update_data(self, ctx, server_id, channel_object, message_object, reaction, role_object, key):
        message_id = message_object.id
        try:
            await message_object.add_reaction(reaction)  # adds reaction to message
        except Exception:
            await ctx.send("Could not add reaction since message does not exist")
        data = {"server_id": server_id,
                "message_id": message_id,
                "channel_id": channel_object.id,
                "reaction": reaction,
                "role_id": role_object.id}
        # if document does not already exist
        if not db.reactive_roles.find_one(data):
            db.reactive_roles.insert_one(data)  # insert document data
            db.reactive_roles.update_one(data, {"$set": {"key": key}})  # index data with a unique key
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name='New Reaction Role Set!', icon_url=self.client.user.avatar_url)
            embed.set_thumbnail(url=self.client.user.avatar_url)
            embed.add_field(name='🔑 Key', value=key, inline=False)  # Key
            embed.add_field(name='📺 Channel', value=channel_object.mention, inline=False)  # Mentioned Channel
            embed.add_field(name='💬 Message', value=message_id, inline=False)  # Message ID
            embed.add_field(name='🎨 Reaction', value=reaction, inline=False)  # Reaction
            embed.add_field(name='🏷 Role', value=role_object.mention, inline=False)  # Mentioned Role
            await ctx.send(embed=embed)  # sends the embeded message
        else:
            await ctx.send("This set of arguments is already activated.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        reaction = payload.emoji.name
        channel = self.client.get_channel(payload.channel_id)
        guild = channel.guild
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)
        # if not HuskyBot
        if member != self.client.user:
            server_id = guild.id
            specs = {"server_id": server_id, "message_id": message.id, "reaction": reaction}
            # if message is a reaction role message
            if db.reactive_roles.find_one(specs):
                for doc in db.reactive_roles.find(specs):
                    role_id = doc["role_id"]
                role_object = guild.get_role(role_id)
                await member.add_roles(role_object)  # adds role to user

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        reaction = payload.emoji.name
        channel = self.client.get_channel(payload.channel_id)
        guild = channel.guild
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)
        # if not HuskyBot
        if member != self.client.user:
            server_id = guild.id
            specs = {"server_id": server_id, "message_id": message.id, "reaction": reaction}
            # if message is a reaction role message
            if db.reactive_roles.find_one(specs):
                for doc in db.reactive_roles.find(specs):
                    role_id = doc["role_id"]
                role_object = guild.get_role(role_id)
                await member.remove_roles(role_object)  # removes role from user

    # creates a new reaction role
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newrr(self, ctx, *args):
        self.__init__(self.client)  # re-intialize variables
        alphabet = string.ascii_letters + string.digits + "-_"
        key = ''.join(random.choice(alphabet) for i in range(9))
        while not self.unique_key:
            # if key is not already in database
            if not db.reactive_roles.find_one({"key": key}):
                self.unique_key = True
            else:
                key = ''.join(random.choice(alphabet) for i in range(9))
        try:
            guild = ctx.guild
            server_id = guild.id
            channel = args[0]
            # get channel object
            for serverChannel in guild.channels:
                # if given given channel was a mentioned channel
                if channel[2:len(channel) - 1] == str(serverChannel.id):
                    channel_id = serverChannel.id
                    self.valid_channel = True
                    break
                # if given channel was a channel name
                elif channel == serverChannel.name:
                    channel_id = serverChannel.id
                    self.valid_channel = True
                    break
            message_id = int(args[1])  # try casting to int to check if it's a number
            # if channel name/id is in server's list of channel name/ids
            if self.valid_channel:
                channel_object = self.client.get_channel(channel_id)
                try:
                    message_object = await channel_object.fetch_message(message_id)
                    self.valid_message_id = True
                # if message was not succesfully retrieved
                except Exception:
                    await ctx.send("Given message could not be retreived")
            else:
                await ctx.send("Given channel is not valid")
            reaction = args[2]
            self.valid_emoji = True
            # load json of valid unicode emojis
            # emojiJson = "https://gist.githubusercontent.com/Vexs/629488c4bb4126ad2a9909309ed6bd71/raw/da8c23f4a42f3ad7cf829398b89bda5347907fef/emoji_map.json"
            # with urllib.request.urlopen(emojiJson) as url:
            #     data = json.loads(url.read().decode())
            # check if reaction is a valid emoji
            # for emoji in data:
            #     if reaction == data[emoji]:
            #         self.valid_emoji = True
            #         break
            # if not a valid emoji
            if not self.valid_emoji:
                await ctx.send("Not a valid emoji")
            role = args[3]
            # get role object
            for serverRole in ctx.guild.roles:
                # if given role was a mentioned role
                if role[3:len(role) - 1] == str(serverRole.id):
                    role_object = serverRole
                    self.valid_role = True
                    break
                # if given role was a role name
                elif role == serverRole.name:
                    role_object = serverRole
                    self.valid_role = True
                    break
            # if role name/id is not in server's list of role name/ids
            if not self.valid_role:
                await ctx.send("Given role is not valid")
            if self.valid_channel and self.valid_role and self.valid_message_id and self.valid_emoji:
                try:
                    await self.update_data(ctx, server_id, channel_object, message_object, reaction, role_object, key)
                except Exception:
                    await ctx.send("Error loading data into databases")
        # if 4 arguments were not given
        except IndexError:
            await ctx.send('Not enough arguments')
        # if message id was not a number
        except ValueError:
            await ctx.send("The given message id must be a number")

    # fetches all the reactions, roles, keys for a given message_id
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def fetchrr(self, ctx, *args):
        guild = ctx.guild
        try:
            server_id = guild.id
            message_id = int(args[0])  # try casting to an int to check if it's a number
        except IndexError:
            await ctx.send("Message ID not given")
        except ValueError:
            await ctx.send("The given message id must be a number")
        key_react_dict = {}
        # build a dictionary of keys corresponding to reactions and roles for given message_id
        for doc in db.reactive_roles.find({"server_id": server_id, "message_id": message_id}):
            key = doc["key"]
            reaction = doc["reaction"]
            role_id = doc["role_id"]
            role = guild.get_role(role_id).mention
            key_react_dict[key] = [reaction, role]
        # if dictionary is not empty
        if key_react_dict:
            embed = embed = discord.Embed(
                description=(f"Message ID: `{message_id}`"),
                colour=discord.Colour.red())
            embed.set_author(name='Keys and Reactions!', icon_url=self.client.user.avatar_url)
            # create a new field for the embeded message for each item with a key, reaction, and role
            for key in key_react_dict:
                reaction = key_react_dict[key][0]
                role = key_react_dict[key][1]
                embed.add_field(name=f'`{key}`', value=f'<{reaction}>\n{role}', inline=True)
            await ctx.send(embed=embed)  # sends the embeded message
        else:
            await ctx.send("There are no reaction roles set for the given message id")

    # removes a reaction role from a message tied to the given key
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removerr(self, ctx, key):
        # if key exists
        if db.reactive_roles.find_one({"key": key}):
            for doc in db.reactive_roles.find({"key": key}):
                channel_id = doc["channel_id"]
                message_id = doc["message_id"]
                reaction = doc["reaction"]
            channel_object = self.client.get_channel(channel_id)
            message_object = await channel_object.fetch_message(message_id)
            await message_object.remove_reaction(reaction, self.client.user)  # unreact from message
            db.reactive_roles.remove({"key": key})  # delete document from database
            await ctx.send(f"Removed reaction role of key `{key}`")
        else:
            await ctx.send("There are no reaction roles with the given key")

    # removes all reaction roles from the given message
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeallrr(self, ctx, message_id):
        server_id = ctx.guild.id
        try:
            message_id = int(message_id)
            # if message_id exists for server
            if db.reactive_roles.find_one({"server_id": server_id, "message_id": message_id}):
                for doc in db.reactive_roles.find({"server_id": server_id, "message_id": message_id}):
                    key = doc["key"]
                    channel_id = doc["channel_id"]
                    message_id = doc["message_id"]
                    reaction = doc["reaction"]
                    channel_object = self.client.get_channel(channel_id)
                    message_object = await channel_object.fetch_message(message_id)
                    await message_object.remove_reaction(reaction, self.client.user)  # unreact from message
                    db.reactive_roles.remove({"key": key})  # delete document from database
                await ctx.send(f"Removed all reaction roles from message id: `{message_id}`")
            else:
                await ctx.send("There are no reaction roles for the given message")
        except ValueError:
            await ctx.send("Message ID must be a number")

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
