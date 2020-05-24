import discord
import os
import pymongo
from discord.ext import commands
from pymongo.collection import Collection
from typing import List, Optional

from checks import is_admin, is_mod
from data.ids import (
    ANNOUNCEMENTS_CHANNEL_ID,
    COURSE_REGISTRATION_CHANNEL_ID,
    HALL_OF_FAME_CHANNEL_ID,
    RULES_CHANNEL_ID,
)

DB_CONNECTION_URL = os.environ["DB_CONNECTION_URL"]
mongoClient = pymongo.MongoClient(DB_CONNECTION_URL)
sent_messages: Collection = mongoClient.hall_of_fame.sent_messages


class HallOfFame(commands.Cog):
    """Handles the automation behind the hall-of-fame channel.
    If at least [self.reaction_threshold] reactions with the 🏆 emoji are added to a
    message or a moderator reacts to a message with that emoji then an embedded message
    with the content of the message, a link to the channel, and a link to the message
    are posted in the hall-of-fame channel.

    Note: If the user who reacts to the message is the same person who sent it,
    it will not count.

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
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.reaction_threshold: int = 5
        self.hof_emoji: str = "🏆"

    @commands.check_any(is_admin(), is_mod())
    @commands.command(aliases=["setHOFThreshold"])
    async def set_hof_threshold(self, ctx: commands.Context, threshold: int) -> None:
        """Sets the new reaction threshold."""
        await ctx.send(
            f"Hall of Fame reaction threshold set to `{threshold}` from `{self.reaction_threshold}`"
        )
        self.reaction_threshold = threshold

    @commands.Cog.listener()
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
        guild_id: Optional[int] = payload.guild_id
        if guild_id is None:
            return

        channel_id: int = payload.channel_id
        BLACKLISTED_CHANNELS = {
            ANNOUNCEMENTS_CHANNEL_ID,
            COURSE_REGISTRATION_CHANNEL_ID,
            HALL_OF_FAME_CHANNEL_ID,
            RULES_CHANNEL_ID,
        }
        if channel_id in BLACKLISTED_CHANNELS:
            return

        emoji: discord.PartialEmoji = payload.emoji
        if emoji.name != self.hof_emoji:
            return

        message_id: int = payload.message_id
        if sent_messages.find_one({"guild_id": guild_id, "messages": message_id}):
            return

        guild: discord.Guild = self.client.get_guild(guild_id)
        channel: discord.TextChannel = guild.get_channel(channel_id)
        message: discord.Message = await channel.fetch_message(message_id)
        member: discord.Member = payload.member
        author: discord.Member = message.author
        if author == member:
            return

        mod: Optional[discord.Role] = discord.utils.get(member.roles, name="Moderator")
        send_message: bool = False
        if mod:
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
            HALL_OF_FAME_CHANNEL: discord.TextChannel = guild.get_channel(
                HALL_OF_FAME_CHANNEL_ID
            )
            embed = discord.Embed(
                colour=discord.Colour.red(), timestamp=message.created_at,
            )
            embed.set_author(name=author, icon_url=author.avatar_url)
            attachments: List[discord.Attachment] = message.attachments
            if attachments:
                embed.set_image(url=attachments[0].proxy_url)
            message_content: str = message.content
            if len(message_content) > 1024:
                message_content = message_content[:1020] + "..."
            embed.add_field(name="Message", value=message_content or "<No Content>")
            embed.add_field(name="Channel", value=channel.mention)
            embed.add_field(name="Jump To", value=f"[Link]({message.jump_url})")
            embed.set_footer(text=f"Message ID: {message_id}")
            await HALL_OF_FAME_CHANNEL.send(embed=embed)
            sent_messages.update_one(
                {"guild_id": guild_id}, {"$push": {"messages": message_id}}, upsert=True
            )
            sent_messages.create_index("messages")


def setup(client: commands.Bot):
    client.add_cog(HallOfFame(client))
