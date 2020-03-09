import discord
from discord.ext import commands

from ids import SUGGESTIONS_CHANNEL_ID


class Suggestion(commands.Cog):
    def __init__(self, client):
        self.client = client

    # allows users to create suggestions
    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        author = ctx.author
        guild = ctx.guild
        SUGGESTIONS_CHANNEL = self.client.get_channel(SUGGESTIONS_CHANNEL_ID)
        ADMIN_ROLE = discord.utils.get(guild.roles, name='Admin')

        await SUGGESTIONS_CHANNEL.send(f"**{ADMIN_ROLE.mention} {author.mention} suggests:**\n"
                                       f"*{suggestion}*")
        await SUGGESTIONS_CHANNEL.last_message.pin()


def setup(client):
    client.add_cog(Suggestion(client))
