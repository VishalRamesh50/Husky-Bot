import discord
from discord.ext import commands

from ids import SCHEDULES_CHANNEL_ID


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

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Deletes any messages in schedules that are not schedules.

        Parameters
        ----------
        message: `discord.Message`
            The message sent by the user.
        """
        channel: discord.TextChannel = message.channel
        author: discord.Member = message.author
        admin: bool = message.webhook_id is None and author.permissions_in(channel).administrator
        SCHEDULES_CHANNEL: discord.TextChannel = self.client.get_channel(SCHEDULES_CHANNEL_ID)

        if channel == SCHEDULES_CHANNEL:
            # Only allow image based schedules to be sent without being deleted.
            # Admins and HuskyBot can bypass this rule.
            if not (admin or author == self.client.user) and len(message.attachments) == 0:
                await message.delete()
                await channel.send("Only schedules should be sent here.", delete_after=5)


def setup(client):
    client.add_cog(Schedules(client))
