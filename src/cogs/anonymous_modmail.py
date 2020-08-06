import asyncio
import discord
from datetime import datetime
from discord.ext import commands
from typing import Dict, List, Optional, Set, Union

from checks import is_mod
from data.ids import GUILD_ID, MOD_CATEGORY_ID


class AnonymousModmail(commands.Cog):
    """Allows for completely anonymous messages between members and moderators.

    Attributes
    ------------
    client: `commands.Bot`
        The instance of the client connection to Discord.
    user_to_channel: `Dict[int, discord.TextChannel]`
        A mapping of user IDs to ticket channels associated with the open ticket.
    channel_to_user: `Dict[int, discord.User]`
        A mapping of ticket channel IDs to the user associated with the open ticket.
    in_progress_users: `Set[int]`
        A set of user IDs for those who have invoked the ticket command and have yet
        to get it cancelled or closed.
    ticket_count: `int`
        The total number of tickets created since the bot started up.
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_to_channel: Dict[int, discord.TextChannel] = {}
        self.channel_to_user: Dict[int, discord.User] = {}
        self.in_progress_users: Set[int] = set()
        self.ticket_count = 0

    @commands.command()
    @commands.dm_only()
    async def ticket(self, ctx: commands.Context) -> None:
        """Starts an anonymous ticket with the mods.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        guild: discord.Guild = self.client.get_guild(GUILD_ID)
        author: discord.User = ctx.author

        if author.id in self.in_progress_users:
            await ctx.send(
                "You can't start a new ticket. You're already in the middle of one!",
                delete_after=5,
            )
            return

        embed = discord.Embed(
            title="Anonymous Modmail Ticket System",
            description=(
                "You have triggered the anonymous modmail ticket system.\n"
                f"When activated, you can have a conversation with the {guild.name} mods anonymously.\n"
                "Confirm by reacting with a ✅. Cancel with ❌"
            ),
        )
        confirmation_msg: discord.Message = await ctx.send(embed=embed)
        await confirmation_msg.add_reaction("✅")
        await confirmation_msg.add_reaction("❌")
        self.in_progress_users.add(author.id)

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                user == author
                and reaction.message.id == confirmation_msg.id
                and str(reaction) in {"✅", "❌"}
            )

        try:
            reaction, _ = await self.client.wait_for(
                "reaction_add", timeout=60.0, check=check
            )
            if str(reaction) == "✅":
                await ctx.send(
                    "You have confirmed. Send a message to start the conversation."
                )
                self.ticket_count += 1
                MOD_CATEGORY: discord.CategoryChannel = self.client.get_channel(
                    MOD_CATEGORY_ID
                )
                MOD_ROLE: discord.Role = discord.utils.get(
                    guild.roles, name="Moderator"
                )
                ticket_channel: discord.TextChannel = await guild.create_text_channel(
                    f"ticket-{self.ticket_count}",
                    category=MOD_CATEGORY,
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            read_messages=False
                        ),
                        MOD_ROLE: discord.PermissionOverwrite(read_messages=True),
                    },
                    reason="anonymous modmail ticket",
                )
                self.user_to_channel[author.id] = ticket_channel
                self.channel_to_user[ticket_channel.id] = author
                embed = discord.Embed(
                    title="New Ticket",
                    description=f"You can always close the ticket using `{self.client.command_prefix}close`",
                    timestamp=datetime.utcnow(),
                    color=discord.Colour.green(),
                )
                await ticket_channel.send(embed=embed)
            elif str(reaction) == "❌":
                self.in_progress_users.remove(author.id)
                await ctx.send(
                    "Request successfully cancelled. No messages will be sent to the mods."
                )
        except asyncio.TimeoutError:
            self.in_progress_users.remove(author.id)
            await ctx.send("No confirmation received. Cancelled.")

    @commands.Cog.listener()
    async def on_typing(
        self,
        channel: discord.abc.Messageable,
        user: Union[discord.User, discord.Member],
        _,
    ) -> None:
        """Triggers typing effect to the other user via the bot if someone is typing
        to simulate a live conversation.

        Parameters
        -------------
        channel `discord.abc.Messageable`
            The location where the typing originated from.
        user `Union[discord.User, discord.Member]`
            The user that started typing.
        """
        if user.bot:
            return

        target: Union[
            discord.User, discord.TextChannel, None
        ] = self.channel_to_user.get(channel.id, self.user_to_channel.get(user.id))

        if target:
            await target.trigger_typing()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Handles message exchange between user and mods.

        Parameters
        -------------
        message: `discord.Message`
            The message sent
        """
        if message.author.bot:
            return

        if message.guild:
            if self.channel_to_user.get(message.channel.id):
                await self.on_mod_msg(message)
        else:
            if self.user_to_channel.get(message.author.id):
                await self.on_user_message(message)

    async def on_mod_msg(self, message: discord.Message) -> None:
        """Sends a message from the mods to the user who created a ticket.

        Parameters
        -------------
        message: `discord.Message`
            The message sent by the mods to be sent to the ticket user.
        """
        ticket_user: discord.User = self.channel_to_user[message.channel.id]
        files: List[discord.File] = [await a.to_file() for a in message.attachments]
        await ticket_user.send(
            f"__{message.author.name}:__ {message.content}", files=files
        )

    async def on_user_message(self, message: discord.Message) -> None:
        """Sends a message to the mods anonymously.

        Parameters
        -------------
        message: `discord.Message`
            The message sent by the ticket user to be sent to the mods.
        """
        ticket_channel: discord.TextChannel = self.user_to_channel[message.author.id]
        files: List[discord.File] = [await a.to_file() for a in message.attachments]
        await ticket_channel.send(
            f"__Anonymous User:__ {message.clean_content}", files=files
        )

    @commands.command()
    @commands.guild_only()
    @is_mod()
    async def close(self, ctx: commands.Context) -> None:
        """Allows mods to close a ticket if one exists. When a ticket is closed, any
        messages sent by the user who opened the ticket to the bot's DMs will not
        be sent to the mods anymore and no messages sent by the mods will be sent to the
        user.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        ticket_channel: discord.TextChannel = ctx.channel
        ticket_user: Optional[discord.User] = self.channel_to_user.get(
            ticket_channel.id
        )
        if ticket_user:
            await self.close_ticket(ctx.author, ticket_user, ticket_channel)
        else:
            await ctx.send("A live ticket does not exist in this channel to be closed.")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Closes ticket if the ticket channel is ever deleted before the ticket was closed.

        Parameters
        -------------
        channel: `discord.abc.GuildChannel`
            The channel that was deleted.
        """
        ticket_user: Optional[discord.User] = self.channel_to_user.get(channel.id)
        if ticket_user:
            ticket_channel: discord.TextChannel = self.user_to_channel[ticket_user.id]
            async for entry in ticket_channel.guild.audit_logs(
                action=discord.AuditLogAction.channel_delete, limit=1
            ):
                mod: Union[discord.Member, discord.User] = entry.user
            await self.close_ticket(mod, ticket_user, ticket_channel, deleted=True)

    async def close_ticket(
        self,
        mod_closed: Union[discord.User, discord.Member],
        ticket_user: discord.User,
        ticket_channel: discord.TextChannel,
        deleted: bool = False,
    ) -> None:
        """Closes the ticket and notifies the members.

        Parameters
        -------------
        mod_closed: `Union[discord.User, discord.Member]`
            The moderator who closed the ticket.
        ticket_user: `discord.User`
            The user who created the ticket.
        ticket_channel: `discord.TextChannel`
            The channel the moderators used to send messages to the ticket_user
        deleted: `bool`
            A flag indicating whether the ticket_channel was deleted or not.
        """
        del self.user_to_channel[ticket_user.id]
        del self.channel_to_user[ticket_channel.id]
        self.in_progress_users.remove(ticket_user.id)

        embed = discord.Embed(
            title="Ticket Closed",
            description=f"This ticket was closed by {mod_closed.name}.\n",
            timestamp=datetime.utcnow(),
            color=discord.Colour.red(),
        )
        if deleted:
            await mod_closed.send(
                "You deleted a ticket channel without closing it. "
                f"Remember to close with `{self.client.command_prefix}close` next time."
            )
        else:
            await ticket_channel.send(embed=embed)

        embed.description += (
            "Any message you send in here will no longer be sent to mods."
        )
        await ticket_user.send(embed=embed)


def setup(client):
    client.add_cog(AnonymousModmail(client))
