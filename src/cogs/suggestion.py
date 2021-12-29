import discord
from discord.ext import commands

from client.bot import Bot, ChannelType
from utils import required_configs


class Suggestion(commands.Cog):
    """Controls the ability to make visible suggestions."""

    def __init__(self, client: Bot):
        self.client = client

    @commands.guild_only()
    @commands.command()
    @required_configs(ChannelType.SUGGESTIONS)
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
        SUGGESTIONS_CHANNEL: discord.TextChannel = self.client.get_suggestions_channel(
            guild.id
        )

        ADMIN_ROLE = discord.utils.get(guild.roles, name="Admin")

        await SUGGESTIONS_CHANNEL.send(
            f"**{ADMIN_ROLE.mention} {ctx.author.mention} suggests:**\n"
            f"*{suggestion}*"
        )
        await SUGGESTIONS_CHANNEL.last_message.pin()


def setup(client: Bot):
    client.add_cog(Suggestion(client))
