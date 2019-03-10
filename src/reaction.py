import discord
from discord.ext import commands
import pymongo
import string
import random
import json
import urllib.request
import os
if os.path.isfile("src/creds.py"):
    from creds import dbUsername, dbPassword  # mongodb username and password
else:
    dbUsername = os.environ["dbUsername"]  # mongodb username from Heroku
    dbPassword = os.environ["dbPassword"]  # mongodb username from Heroku

# connect to mongodb cluster
mongoClient = pymongo.MongoClient(f"mongodb://{dbUsername}:{dbPassword}"
                                  "@huksybot-shard-00-00-d1jta.mongodb.net:27017,"
                                  "huksybot-shard-00-01-d1jta.mongodb.net:27017,"
                                  "huksybot-shard-00-02-d1jta.mongodb.net:27017"
                                  "/test?ssl=true&replicaSet=HuksyBot-shard-0&"
                                  "authSource=admin&retryWrites=true")
db = mongoClient.reactions  # use the reactions database


class Reaction:
    def __init__(self, client):
        self.client = client
        self.unique_key = False
        self.valid_channel = False
        self.valid_role = False
        self.valid_message_id = False
        self.valid_emoji = False

    async def update_data(self, server_id, channel_id, message_object, message_id, reaction, role_id, key):
        try:
            await self.client.add_reaction(message_object, reaction)  # adds reaction to message
        except Exception:
            await self.client.say("Could not add reaction since message does not exist")
        data = {"server_id": server_id,
                "message_id": message_id,
                "channel_id": channel_id,
                "reaction": reaction,
                "role_id": role_id}
        # if document does not already exist
        if not db.reactive_roles.find_one(data):
            db.reactive_roles.insert_one(data)  # insert document data
            db.reactive_roles.update_one(data, {"$set": {"key": key}})  # index data with a unique key
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name='New Reaction Role Set!', icon_url=self.client.user.avatar_url)
            embed.set_thumbnail(url=self.client.user.avatar_url)
            embed.add_field(name='🔑 Key', value=key, inline=False)  # Key
            embed.add_field(name='📺 Channel', value='<#'+channel_id+'>', inline=False)  # Mentioned Channel
            embed.add_field(name='💬 Message', value=message_id, inline=False)  # Message ID
            embed.add_field(name='🎨 Reaction', value=reaction, inline=False)  # Reaction
            embed.add_field(name='🏷 Role', value='<@&'+role_id+'>', inline=False)  # Mentioned Role
            await self.client.say(embed=embed)  # sends the embeded message
        else:
            await self.client.say("This set of arguments is already activated.")

    async def on_socket_raw_receive(self, raw_msg):
        try:
            if not isinstance(raw_msg, str):
                return
            msg = json.loads(raw_msg)
            type = msg.get("t")
            data = msg.get("d")
            if not data:
                return
            emoji = data.get("emoji")
            user_id = data.get("user_id")
            user_object = await self.client.get_user_info(user_id)
            message_id = data.get("message_id")
            channel_id = data.get("channel_id")
            channel_object = self.client.get_channel(channel_id)
            message_object = await self.client.get_message(channel_object, message_id)
            if type == "MESSAGE_REACTION_ADD":
                await self.user_reacted(emoji["name"], user_object, message_object)
            elif type == "MESSAGE_REACTION_REMOVE":
                await self.user_unreacted(emoji["name"], user_object, message_object)
        except discord.errors.HTTPException:
            pass

    async def user_reacted(self, reaction, user, message):
        # if not bot
        if user != self.client.user:
            # convert user object to member object
            for member in message.server.members:
                if user.name == member.name:
                    user = member
                    break
            server_id = message.server.id
            specs = {"server_id": server_id, "message_id": message.id, "reaction": reaction}
            # if message is a reaction role message
            if db.reactive_roles.find_one(specs):
                for doc in db.reactive_roles.find(specs):
                    role_id = doc["role_id"]
                role_object = discord.utils.get(message.server.roles, id=role_id)
                await self.client.add_roles(user, role_object)  # adds role to user

    async def user_unreacted(self, reaction, user, message):
        # if not bot
        if user != self.client.user:
            # convert user object to member object
            for member in message.server.members:
                if user.name == member.name:
                    user = member
                    break
            server_id = message.server.id
            specs = {"server_id": server_id, "message_id": message.id, "reaction": reaction}
            # if message is a reaction role message
            if db.reactive_roles.find_one(specs):
                for doc in db.reactive_roles.find(specs):
                    role_id = doc["role_id"]
                role_object = discord.utils.get(message.server.roles, id=role_id)
                await self.client.remove_roles(user, role_object)

    @commands.command(pass_context=True)
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
            server_id = ctx.message.server.id
            channel = args[0]
            # get channel object
            for serverChannel in self.client.get_all_channels():
                # if given given channel was a mentioned channel
                if channel[2:len(channel)-1] == serverChannel.id:
                    channel_id = serverChannel.id
                    self.valid_channel = True
                    break
                # if given channel was a channel name
                elif channel == serverChannel.name:
                    channel_id = serverChannel.id
                    self.valid_channel = True
                    break
            message_id = str(int(args[1]))  # try casting to int to check if it's a number
            # if channel name/id is in server's list of channel name/ids
            if self.valid_channel:
                channel_object = self.client.get_channel(channel_id)
                try:
                    message_object = await self.client.get_message(channel_object, message_id)
                    self.valid_message_id = True
                # if message was not succesfully retrieved
                except Exception:
                    await self.client.say("Given message could not be retreived")
            else:
                await self.client.say("Given channel is not valid")
            reaction = args[2]
            # load json of valid unicode emojis
            emojiJson = "https://gist.githubusercontent.com/Vexs/629488c4bb4126ad2a9909309ed6bd71/raw/da8c23f4a42f3ad7cf829398b89bda5347907fef/emoji_map.json"
            with urllib.request.urlopen(emojiJson) as url:
                data = json.loads(url.read().decode())
            # check if reaction is a valid emoji
            for emoji in data:
                if reaction == data[emoji]:
                    self.valid_emoji = True
                    break
            # if not a valid emoji
            if not self.valid_emoji:
                await self.client.say("Not a valid emoji")
            role = args[3]
            # get role object
            for serverRole in ctx.message.server.roles:
                # if given role was a mentioned role
                if role[3:len(role)-1] == serverRole.id:
                    role_id = serverRole.id
                    self.valid_role = True
                    break
                # if given role was a role name
                elif role == serverRole.name:
                    role_id = serverRole.id
                    self.valid_role = True
                    break
            # if role name/id is not in server's list of role name/ids
            if not self.valid_role:
                await self.client.say("Given role is not valid")
            if self.valid_channel and self.valid_role and self.valid_message_id and self.valid_emoji:
                try:
                    await self.update_data(server_id, channel_id, message_object, message_id, reaction, role_id, key)
                except Exception:
                    await self.client.say("Error loading data into databases")
        # if 4 arguments were not given
        except IndexError:
            await self.client.say('Not enough arguments')
        # if message id was not a number
        except ValueError:
            await self.client.say("The given message id must be a number")

    @commands.command(pass_context=True)
    async def fetchrr(self, ctx, *args):
        try:
            server_id = ctx.message.server.id
            message_id = str(int(args[0]))  # try casting to an int to check if it's a number
        except IndexError:
            await self.client.say("Message ID not given")
        except ValueError:
            await self.client.say("The given message id must be a number")
        key_react_dict = {}
        # build a dictionary of keys corresponding to reactions and roles for given message_id
        for doc in db.reactive_roles.find({"server_id": server_id, "message_id": message_id}):
            key = doc["key"]
            reaction = doc["reaction"]
            role = '<@&'+doc["role_id"]+'>'
            key_react_dict[key] = [reaction, role]
        # if dictionary is not empty
        if key_react_dict:
            embed = embed = discord.Embed(
                description=(f"Message ID: `{message_id}`"),
                colour=discord.Colour.red())
            embed.set_author(name='Keys and Reactions!', icon_url=self.client.user.avatar_url)
            # create a new field for the embeded message for each item with a key, reaction, and role
            for key in key_react_dict:
                embed.add_field(name=f'`{key}`', value=f'<{key_react_dict[key][0]}>\n{key_react_dict[key][1]}', inline=True)
            await self.client.say(embed=embed)  # sends the embeded message
        else:
            await self.client.say("There are no reaction roles set for the given message id")

    @commands.command()
    async def removerr(self, key):
        # if key exists
        if db.reactive_roles.find_one({"key": key}):
            for doc in db.reactive_roles.find({"key": key}):
                channel_id = doc["channel_id"]
                message_id = doc["message_id"]
                reaction = doc["reaction"]
            channel_object = self.client.get_channel(channel_id)
            message_object = await self.client.get_message(channel_object, message_id)
            await self.client.remove_reaction(message_object, reaction, self.client.user)  # unreact from message
            db.reactive_roles.remove({"key": key})  # delete document from database
            await self.client.say(f"Removed reaction role of key `{key}`")
        else:
            await self.client.say("There are no reaction roles with the given key")


def setup(client):
    client.add_cog(Reaction(client))
