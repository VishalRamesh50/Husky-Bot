import discord
from discord.ext import commands

from data.ids import SUGGESTIONS_CHANNEL_ID


class Suggestion(commands.Cog):
    """Controls the ability to make visible suggestions."""

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.guild_only()
    @commands.command()
    async def suggest(self, ctx: commands.Context, *, suggestion: str) -> None:
        """Will post a formatted message of the suggestion made by a user in
        the suggestions channel, pings the Admins and pins the message.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        suggestion: `str`
            The suggestion the the user made.
        """
        guild: discord.Guild = ctx.guild
        SUGGESTIONS_CHANNEL = guild.get_channel(SUGGESTIONS_CHANNEL_ID)
        ADMIN_ROLE = discord.utils.get(guild.roles, name="Admin")

        await SUGGESTIONS_CHANNEL.send(
            f"**{ADMIN_ROLE.mention} {ctx.author.mention} suggests:**\n"
            f"*{suggestion}*"
        )
        await SUGGESTIONS_CHANNEL.last_message.pin()


def setup(client: commands.Bot):
    client.add_cog(Suggestion(client))
