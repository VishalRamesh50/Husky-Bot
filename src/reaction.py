from discord.ext import commands
import json
import os
os.chdir('Husky-Bot/src/')


class Reaction:
    def __init__(self, client):
        self.client = client

    async def update_data(self, roles, server_id, channel, message_id, emoji, role):
        if server_id not in roles:
            roles[server_id] = {}
        if message_id not in roles[server_id]:
            roles[server_id][message_id] = {}
        roles[server_id][message_id]['channel'] = channel
        roles[server_id][message_id]['emoji'] = emoji
        roles[server_id][message_id]['role'] = role

    '''
    async def on_reaction_add(self, reaction, user):
        with open('reaction_roles.json', 'r') as f:
            roles = json.load(f)

        # await self.addRole(roles, reaction, user)

        with open('reaction_roles.json', 'w') as f:
            json.dump(roles, f)
    '''

    @commands.command(pass_context=True)
    async def newrr(self, ctx, *args):
        try:
            server_id = ctx.message.server.id
            channel = args[0]
            message_id = args[1]
            emoji = args[2]
            role = args[3]
        except IndexError:
            await self.client.say('Not enough arguments')

        try:
            with open('reaction_roles.json', 'r') as f:
                roles = json.load(f)
        except FileNotFoundError:
            print('File not found.')

        await self.update_data(roles, server_id, channel, message_id, emoji, role)

        try:
            with open('reaction_roles.json', 'w') as f:
                json.dump(roles, f)
        except FileNotFoundError:
            print('File not found')

    @commands.command()
    async def showJson(self, *args):
        try:
            server_id = args[0]
            message_id = args[1]
            field = args[2]
        except IndexError:
            await self.client.say('Not enough arguments')
        try:
            with open('reaction_roles.json', 'r') as f:
                roles = json.load(f)
        except FileNotFoundError:
            print('File not found.')
        await self.client.say(roles[server_id][message_id][field])


def setup(client):
    client.add_cog(Reaction(client))
