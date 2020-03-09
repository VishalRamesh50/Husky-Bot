import os
import pymongo
from discord.ext import commands

from ids import SUPERSECSEE_ID as TOM_ID

DB_CONNECTION_URL = os.environ["DB_CONNECTION_URL"]

# connect to mongodb cluster
mongoClient = pymongo.MongoClient(DB_CONNECTION_URL)
db = mongoClient.aprilFools  # use the april fools database

aprilFoolsMsg = "Wh͢͟ȩ̴̕n͟ ̡̢͢E͠v̀͏̨e͏̕ŗ͜y͏̛́on̷͞͞e̵͜͝ ̧͢is ͝͠T̕͠om̕,̛ ̡́No ̧͞Ǫ̶n͏͞é̵͡ ̡̡is̶̢ ̴̨T̸͜͟o͜͏́m̨"


class AprilFools(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.toggle = False

    # starts AprilFools
    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def createAF(self, ctx):
        self.toggle = True
        guild = ctx.guild
        server_id = guild.id
        tom_member = guild.get_member(TOM_ID)
        new_nickname = tom_member.nick
        if new_nickname is None:
            new_nickname = tom_member.display_name
        for member in guild.members:
            member_id = member.id
            old_nickname = member.nick
            if old_nickname is None:
                old_nickname = member.display_name
            data = {"server_id": server_id,
                    "user_id": member_id,
                    "old_nickname": old_nickname,
                    "new_nickname": new_nickname}
            # if combo not in database add it
            if not db.updateNicknames.find_one({"server_id": server_id, "user_id": member_id}):
                db.updateNicknames.insert_one(data)
        await ctx.send("Database succesfully created")

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def initAF(self, ctx):
        guild = ctx.guild
        server_id = guild.id
        await ctx.send(aprilFoolsMsg)
        for member in guild.members:
            specs = {"server_id": server_id, "user_id": member.id}
            if db.updateNicknames.find_one(specs):
                for doc in db.updateNicknames.find(specs):
                    new_nickname = doc["new_nickname"]
                    try:
                        await member.edit(nick=new_nickname)
                        print(member.name, 'name changed')
                    except Exception:
                        pass
        print('Finished changing all members')

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def revertAF(self, ctx):
        self.toggle = False
        guild = ctx.guild
        server_id = guild.id
        tom_member = guild.get_member(TOM_ID)
        new_nickname = tom_member.nick
        if new_nickname is None:
            new_nickname = tom_member.display_name
        for member in guild.members:
            specs = {"server_id": server_id, "user_id": member.id}
            if db.updateNicknames.find_one(specs):
                for doc in db.updateNicknames.find(specs):
                    old_nickname = doc["old_nickname"]
                    try:
                        await member.edit(nick=old_nickname)
                        print(member.name, 'reverted')
                    except Exception:
                        pass
        print('Finished reverting April Fools')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if self.toggle:
            guild = after.guild
            server_id = guild.id
            specs = {"server_id": server_id, "user_id": after.id}
            if db.updateNicknames.find_one(specs):
                for doc in db.updateNicknames.find(specs):
                    new_nickname = doc["new_nickname"]
                    old_nickname = doc["old_nickname"]
                    if after.nick != new_nickname:
                        try:
                            await after.edit(nick=new_nickname)
                            print(old_nickname, 'tried changing name')
                        except Exception:
                            pass

    @commands.command(pass_context=True)
    async def toggleAF(self, ctx):
        self.toggle = not self.toggle
        await ctx.send(f"April Fools:{self.toggle}")


def setup(client):
    client.add_cog(AprilFools(client))
