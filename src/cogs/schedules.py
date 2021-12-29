import discord
from discord.ext import commands

from client.bot import Bot, ChannelType
from utils import required_configs


class Schedules(commands.Cog):
    """Handles sending the it be like that gif.

    Attributes
    ----------
    client : `commands.Bot`
        a client connection to Discord to interact with the Discord WebSocket and APIs

    Methods
    -------
    on_message(ctx: message: `discord.Message`)
        Deletes any messages in schedules that are not schedules.
    """

    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    @required_configs(ChannelType.SCHEDULES)
    async def on_message(self, message: discord.Message) -> None:
        """Deletes any messages in schedules that are not schedules.

        Parameters
        ----------
        message: `discord.Message`
            The message sent by the user.
        """
        guild: discord.Guild = message.guild
        channel: discord.TextChannel = message.channel
        author: discord.Member = message.author
        SCHEDULES_CHANNEL: discord.TextChannel = self.client.get_schedules_channel(
            guild.id
        )

        if channel == SCHEDULES_CHANNEL:
            admin: bool = author.permissions_in(channel).administrator
            # Only allow image based schedules to be sent without being deleted.
            # Admins and HuskyBot can bypass this rule.
            if (
                not (admin or author == self.client.user)
                and len(message.attachments) == 0
            ):
                await message.delete()
                await channel.send(
                    "Only schedules should be sent here.", delete_after=5
                )


def setup(client):
    client.add_cog(Schedules(client))
