import discord
from collections import defaultdict
from discord.ext import commands
from typing import Dict, List, Optional, Set, Union

from checks import is_admin, is_mod
from client.bot import Bot, ChannelType
from utils import required_configs


class HallOfFame(commands.Cog):
    """Handles the automation behind the hall-of-fame channel.
    If at least [self.reaction_threshold] reactions with the 🏆 emoji are added to a
    message, then an embedded message with the content of the message, a link to the
    channel, and a link to the message are posted in the hall-of-fame channel.

    Note:
        - If the user who reacts to the message is the same person who sent it,
    it will not count.
        - If a moderator reacts with the designated mod hall-of-fame emoji, then it
    will automatically be send in the hall-of-fame channel regardless of emoji count.

    Attributes
    ----------
    client : `commands.Bot`
        a client connection to Discord to interact with the Discord WebSocket and APIs
    reaction_threshold: `int`
        the number of emojis that need to be reacted with (excluding the user who sent
        the message) in order to enter the hall-of-fame.
    hof_emoji: `str`
        The emoji which is tracked in order to determine whether to send it to the
        hall-of-fame or not.
    mod_hof_emoji: `str`
        An override emoji. When reacted to a message with it will automatically be sent
        in hall-of-fame regardless of the emoji count on the current message.
    """

    def __init__(self, client: Bot):
        self.client = client
        self.reaction_threshold: int = 7
        self.hof_emoji: str = "🏆"
        self.mod_hof_emoji: str = "🏅"
        self.hof_blacklist: Dict[int, Set[int]] = defaultdict(set)
        for document in self.client.db.get_hof_blacklist():
            guild_id: int = document["guild_id"]
            channels: List[int] = document["channels"]
            self.hof_blacklist[guild_id] = set(channels)

    @commands.is_owner()
    @commands.command(aliases=["setHOFThreshold"])
    @required_configs(ChannelType.HOF)
    async def set_hof_threshold(self, ctx: commands.Context, threshold: int) -> None:
        # TODO: Set this in the database so that it is a persistent configuration
        """Sets the new reaction threshold."""
        await ctx.send(
            f"Hall of Fame reaction threshold set to `{threshold}` from `{self.reaction_threshold}`"
        )
        self.reaction_threshold = threshold

    @commands.check_any(is_admin(), is_mod())
    @commands.command(aliases=["addHOFBlacklist"])
    @required_configs(ChannelType.HOF)
    async def add_hof_blacklist(
        self, ctx: commands.Context, channel: Union[discord.TextChannel, discord.Thread]
    ):
        guild: discord.Guild = ctx.guild
        if channel.id in self.hof_blacklist[guild.id]:
            return await ctx.send("This channel is already being blacklisted by HOF.")
        self.client.db.add_to_hof_blacklist(guild.id, channel.id)
        self.hof_blacklist[guild.id].add(channel.id)
        await ctx.send(f"{channel.mention} has been added to the HOF blacklist")

    @commands.command(aliases=["removeHOFBlacklist", "rmHOFBlacklist"])
    @required_configs(ChannelType.HOF)
    async def remove_hof_blacklist(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        guild: discord.Guild = ctx.guild
        if channel.id not in self.hof_blacklist[guild.id]:
            return await ctx.send(
                "This channel was never blacklisted in the first place"
            )
        self.client.db.remove_from_hof_blacklist(ctx.guild.id, channel.id)
        self.hof_blacklist[ctx.guild.id].remove(channel.id)
        await ctx.send(f"{channel.mention} has been removed from the HOF blacklist")

    @commands.command(aliases=["listHOFBlacklist", "lsHOFBlacklist"])
    @required_configs(ChannelType.HOF)
    async def list_hof_blacklist(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        blacklisted_channel_mentions: List[str] = [
            guild.get_channel_or_thread(channel_id).mention
            for channel_id in self.hof_blacklist[guild.id]
        ]
        await ctx.send(
            f"There are {len(blacklisted_channel_mentions)} channels being blacklisted for HOF currently: {','.join(blacklisted_channel_mentions)}"
        )

    @commands.Cog.listener()
    @required_configs(ChannelType.HOF)
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        """Checks if enough reactions were added and if so sends a message
        in the hall-of-fame channel.

        Parameters
        -------------
        payload: `discord.RawReactionActionEvent`
            The reaction payload with information about the event.
        """
        guild_id: int = payload.guild_id
        channel_id: int = payload.channel_id
        if channel_id in self.hof_blacklist[guild_id]:
            return

        emoji: discord.PartialEmoji = payload.emoji
        mod_emoji_used: bool = emoji.name == self.mod_hof_emoji
        if emoji.name != self.hof_emoji and not mod_emoji_used:
            return

        message_id: int = payload.message_id
        if self.client.db.message_in_hof(guild_id, message_id):
            return

        guild: discord.Guild = self.client.get_guild(guild_id)
        channel: Optional[
            Union[discord.abc.GuildChannel, discord.Thread]
        ] = guild.get_channel_or_thread(channel_id)
        message: discord.Message = await channel.fetch_message(message_id)
        member: discord.Member = payload.member
        author: discord.Member = message.author
        if author == member:
            return

        mod: Optional[discord.Role] = discord.utils.get(member.roles, name="Moderator")
        send_message: bool = False
        if mod_emoji_used:
            if not mod:
                return
            else:
                send_message = True
        else:
            reaction: discord.Reaction = next(
                r for r in message.reactions if str(r.emoji) == emoji.name
            )
            reaction_count: int = reaction.count
            if reaction_count > self.reaction_threshold:
                send_message = True
            elif reaction_count == self.reaction_threshold:
                send_message = True
                async for user in reaction.users():
                    if user == author:
                        send_message = False
                        break

        if send_message:
            HALL_OF_FAME_CHANNEL: discord.TextChannel = self.client.get_hof_channel(
                guild_id
            )
            embed = discord.Embed(
                color=discord.Color.red(), timestamp=message.created_at
            )
            embed.set_author(name=author, icon_url=author.display_avatar.url)
            attachments: List[discord.Attachment] = message.attachments
            if attachments:
                embed.set_image(url=attachments[0].proxy_url)
            message_content: str = message.content
            if message_content:
                if len(message_content) > 1024:
                    message_content = message_content[:1020] + "..."
                embed.add_field(name="Message", value=message_content)
            embed.add_field(name="Channel", value=channel.mention)
            embed.add_field(name="Jump To", value=f"[Link]({message.jump_url})")
            embed.set_footer(text=f"Message ID: {message_id}")
            await HALL_OF_FAME_CHANNEL.send(embed=embed)
            self.client.db.add_message_to_hof(guild_id, message_id)


async def setup(client: commands.Bot):
    await client.add_cog(HallOfFame(client))
