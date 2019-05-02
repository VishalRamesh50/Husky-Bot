import discord
from discord.ext import commands
import pymongo
import string
import random
import json
import urllib.request
import os
try:
    from creds import dbUsername, dbPassword  # mongodb username and password
except Exception:
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


class Reaction(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.unique_key = False
        self.valid_channel = False
        self.valid_role = False
        self.valid_message_id = False
        self.valid_emoji = False

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
                if channel[2:len(channel)-1] == str(serverChannel.id):
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
                await ctx.send("Not a valid emoji")
            role = args[3]
            # get role object
            for serverRole in ctx.guild.roles:
                # if given role was a mentioned role
                if role[3:len(role)-1] == str(serverRole.id):
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


def setup(client):
    client.add_cog(Reaction(client))
