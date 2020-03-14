import discord
import string
from discord.ext import commands

from ids import BOT_SPAM_CHANNEL_ID


class ItBeLikeThat(commands.Cog):
    """Handles sending the it be like that gif.

    Attributes
    ----------
    client : `commands.Bot`
        a client connection to Discord to interact with the Discord WebSocket and APIs

    Methods
    -------
    on_message(ctx: message: `discord.Message`)
        Sends the "it be like that" gif anytime those words are in a sentence in any order.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Sends "it be like that" gif anytime those words are in a sentence in any order.

        Parameters
        ----------
        message: `discord.Message`
            The message sent by the user.
        """
        channel: discord.TextChannel = message.channel
        author: discord.Member = message.author
        BOT_SPAM_CHANNEL: discord.TextChannel = self.client.get_channel(BOT_SPAM_CHANNEL_ID)
        IT_BE_LIKE_THAT_GIF = "https://tenor.com/view/it-really-do-be-like-that-sometimes-like-that-sometimes-gif-12424014"

        if not author.bot and channel == BOT_SPAM_CHANNEL:
            content: str = message.content
            # strip out puncuation
            content = content.translate(str.maketrans('', '', string.punctuation))
            IT_BE_LIKE_THAT: set = {'IT', 'BE', 'LIKE', 'THAT'}
            if set(content.upper().split()).issuperset(IT_BE_LIKE_THAT):
                await channel.send(IT_BE_LIKE_THAT_GIF)


def setup(client):
    client.add_cog(ItBeLikeThat(client))
