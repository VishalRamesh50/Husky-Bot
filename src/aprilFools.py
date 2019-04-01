from discord.ext import commands
import pymongo
import time
import os
if os.path.isfile("creds.py"):
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
db = mongoClient.aprilFools  # use the reactions database

TOM_ID = '267792923209236500'
aprilFoolsMsg = "Wh͢͟ȩ̴̕n͟ ̡̢͢E͠v̀͏̨e͏̕ŗ͜y͏̛́on̷͞͞e̵͜͝ ̧͢is ͝͠T̕͠om̕,̛ ̡́No ̧͞Ǫ̶n͏͞é̵͡ ̡̡is̶̢ ̴̨T̸͜͟o͜͏́m̨"


class AprilFools:
    def __init__(self, client):
        self.client = client

    # starts AprilFools
    @commands.command(pass_context=True)
    async def createAF(self, ctx):
        server = ctx.message.server
        server_id = ctx.message.server.id
        tom_member = ctx.message.server.get_member(TOM_ID)
        new_nickname = tom_member.nick
        if new_nickname is None:
            new_nickname = tom_member.display_name
        for member in server.members:
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

    @commands.command(pass_context=True)
    async def initAF(self, ctx):
        server = ctx.message.server
        server_id = ctx.message.server.id
        tom_member = ctx.message.server.get_member(TOM_ID)
        new_nickname = tom_member.nick
        if new_nickname is None:
            new_nickname = tom_member.display_name
        await self.client.say(aprilFoolsMsg)
        for member in server.members:
            print('Member', member.name)
            if (member.nick != new_nickname):
                specs = {"server_id": server_id, "user_id": member.id}
                if db.updateNicknames.find_one(specs):
                    for doc in db.updateNicknames.find(specs):
                        new_nickname = doc["new_nickname"]
                        try:
                            await self.client.change_nickname(member, new_nickname)
                            print('Name changed', member.name)
                        except Exception:
                            pass
        print('Finished changing all members')

    @commands.command(pass_context=True)
    async def revertAF(self, ctx):
        server = ctx.message.server
        server_id = ctx.message.server.id
        tom_member = ctx.message.server.get_member(TOM_ID)
        new_nickname = tom_member.nick
        if new_nickname is None:
            new_nickname = tom_member.display_name
        for member in server.members:
            specs = {"server_id": server_id, "user_id": member.id}
            if db.updateNicknames.find_one(specs):
                for doc in db.updateNicknames.find(specs):
                    old_nickname = doc["old_nickname"]
                    try:
                        await self.client.change_nickname(member, old_nickname)
                        print(member.name, 'reverted')
                    except Exception:
                        pass
        print('Finished reverting April Fools')


def setup(client):
    client.add_cog(AprilFools(client))
