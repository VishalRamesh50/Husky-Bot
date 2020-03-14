import discord
import random
from time import time
from discord.ext import commands

from ids import BOT_SPAM_CHANNEL_ID


class Aoun(commands.Cog):
    """
    Controls the behavior of sending Aoun related images in chat.

    Attributes
    ----------
    client : `commands.Bot`
        a client connection to Discord to interact with the Discord WebSocket and APIs
    last_aoun: `float`
        the last time that an Aoun image was sent in chat (used for cooldown calculations)
    last_warning: `float`
        the last time that a warning message with cooldown info was sent.
    manually_set: `bool`
        Whether the cooldown was manually set or not.
        If set manually cooldown will not be automatically recalculated.
    cooldown: `int`
        The number of seconds to cooldown since the last Aoun image was sent.
    MIN_COOLDOWN: `bool`
        The default minimum amount of seconds to cooldown before the next image can be sent.
        Note: The cooldown can be less than this number if manually set.
    MAX_COOLDOWN: `bool`
        The default maximum amount of seconds to automatically increase the cooldown to.
        Note: The cooldown can be greater than this number if manually set.
    MAX_COOLDOWN_LIMIT: `bool`
        The strict maximum cooldown which is required to wait before sending another image.

    Properties
    ----------
    time_left: `int`
        The time left in seconds till the cooldown is over.
    after_cooldown: `bool`
        If now is after the cooldown limit since the last Aoun message was sent.
    can_warn: `bool`
        A flag which determines if a warning with cooldown info can be sent.

    Methods
    -------
    setACooldown(ctx: commands.Context, cooldown: int)
        Sets a new cooldown rate.
    on_message(ctx: message: `discord.Message`)
        Sends a random Aoun message when a message is sent.
    """

    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.last_aoun: float = time()
        self.last_warning: float = time()
        self.manually_set: bool = False

        # ------------ CONSTANTS -------------
        self.MIN_COOLDOWN: int = 5
        self.MAX_COOLDOWN: int = 60
        self.MAX_COOLDOWN_LIMIT: int = 900
        # ------------------------------------

        self.cooldown: int = self.MIN_COOLDOWN

    @property
    def time_left(self) -> int:
        """The time left in seconds till the cooldown is over.

        Returns
        ----------
        An integer representing the seconds till the cooldown is over.
        """
        return self.cooldown - int(time() - self.last_aoun)

    @property
    def after_cooldown(self) -> bool:
        """Determines if the last aoun message was sent after the cooldown.

        Returns
        ----------
        True if the last aoun message was sent after the cooldown, else False.
        """
        return self.time_left <= 0

    @property
    def can_warn(self) -> bool:
        """If a warning can be sent with information on the cooldown.
        Exists to avoid spamming warning messages everytime someone triggers an Aoun
        message before the cooldown has been passed.

        Returns
        ----------
        True the last time a warning was sent was at least 5 seconds ago, else False.
        """
        return time() - self.last_warning >= 5

    @commands.command()
    @commands.has_any_role('Admin', 'Moderator')
    async def setACooldown(self, ctx: commands.Context, cooldown: int) -> None:
        """Sets a new Aoun cooldown to the given cooldown.
        Must be a positive intger up to 900 seconds.

        Parameters
        ----------
        ctx : `commands.Context`
            A class containing metadata about the command invocation.
        cooldown: `int`
            The new number of seconds to set the cooldown to.
        """

        if cooldown < 0:
            await ctx.send(f'You want negative time? There is such a thing as too much '
                           'Aoun you know. You need a `positive integer`.', delete_after=5)
            return

        if cooldown > self.MAX_COOLDOWN_LIMIT:
            await ctx.send('Chill, this cooldown is too high. Aoun does not approve. '
                           f'Max is `{self.MAX_COOLDOWN_LIMIT} seconds`.', delete_after=5)
            return

        self.cooldown = cooldown
        self.last_aoun = time()
        self.manually_set = True
        await ctx.send(f'New Aoun cooldown: `{self.cooldown} seconds`')

    @commands.command()
    @commands.has_any_role('Admin', 'Moderator')
    async def resetACooldown(self, ctx: commands.Context) -> None:
        """Resets the cooldown and toggles off the `manually_set` flag.

        Parameters
        ----------
        ctx : `commands.Context`
            A class containing metadata about the command invocation.
        """

        self.manually_set = False
        self.cooldown = self.MIN_COOLDOWN
        await ctx.send("The Aoun cooldown was reset", delete_after=5)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Send a random picture of Aoun anytime his name is metioned
        by a user in the bot-spam channel.

        If a message is sent before the cooldown, the cooldown time will increase
        by 5 seconds. If it sent after the cooldown the cooldown time will reset to the
        MIN_COOLDOWN. The cooldown is guaranteed to be within the MIN_COOLDOWN and
        MAX_COOLDOWN range (inclusive) unless it was manually set.

        The cooldown rates will not be adjusted if it was manually set and must be reset
        manually with the `resetACooldown` command to be reset to the normal state.

        The images will only be sent in response to messages sent in the #bot-spam channel
        and will ignore messages from bots.

        Parameters
        ----------
        message: `discord.Message`
            The message sent by the user.
        """

        channel: discord.TextChannel = message.channel
        author: discord.Member = message.author
        BOT_SPAM_CHANNEL: discord.TextChannel = self.client.get_channel(BOT_SPAM_CHANNEL_ID)

        # ignore bots and only check the bot-spam channel
        if not author.bot and channel == BOT_SPAM_CHANNEL:
            content: str = message.content

            AOUN_PICS = ['https://nustudentlife.files.wordpress.com/2016/07/maxresdefault1.jpg',
                         'https://i.redd.it/l2ectyrr30ry.png',
                         'https://i.redd.it/jamxajoqfkhy.png',
                         'https://imgur.com/DWTkyXU.jpg',
                         'https://imgur.com/BdWa9YS.jpg',
                         'https://imgur.com/dYEgEaM.jpg',
                         'https://imgur.com/RTn4rCt.jpg',
                         'https://imgur.com/dK8DFjm.jpg',
                         'https://i.imgur.com/CZxENli.jpg',
                         'https://i.imgur.com/fDyw1Jl.jpg',
                         'https://i.imgur.com/eqTxbiQ.jpg',
                         'https://i.imgur.com/GbyVuHu.jpg',
                         'https://i.imgur.com/jUtM6jo.jpg',
                         'https://imgur.com/48LIGL3.jpg',
                         'https://i.imgur.com/uJkGNKX.png']

            if "AOUN" in content.upper():
                if self.after_cooldown:
                    await channel.send(AOUN_PICS[random.randint(0, len(AOUN_PICS) - 1)])
                    self.last_aoun = time()
                    if not self.manually_set:
                        self.cooldown = self.MIN_COOLDOWN
                else:
                    if not self.manually_set:
                        self.cooldown = min(self.cooldown + 5, self.MAX_COOLDOWN)
                        if self.can_warn:
                            await channel.send(f"Cooldown increased to `{self.cooldown} seconds`.", delete_after=3)
                    if self.can_warn:
                        await channel.send(f"`{self.time_left} seconds` left.", delete_after=3)
                        self.last_warning = time()


def setup(client):
    client.add_cog(Aoun(client))
