import asyncio
import discord
import random
import string
from discord.ext import commands
from typing import Dict, List, Optional, Set, Union

from client.bot import Bot
from checks import is_mod
from utils import PaginatedEmbed


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
    """

    confirm_emoji: str = "✅"
    cancel_emoji: str = "❌"

    def __init__(self, client: Bot):
        self.client = client
        self.user_to_channel: Dict[int, discord.TextChannel] = {}
        self.channel_to_user: Dict[int, discord.User] = {}
        self.in_progress_users: Set[int] = set()

    @commands.command()
    @commands.dm_only()
    async def ticket(self, ctx: commands.Context) -> None:
        """Starts an anonymous ticket with the mods.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        author: discord.User = ctx.author
        if author.id in self.user_to_channel:
            in_progress_guild: discord.Guild = self.user_to_channel[author.id].guild
            return await ctx.send(
                "You can't start a new ticket. You're already in the middle of one with "
                f"**{in_progress_guild.name}** (Server ID: {in_progress_guild.id})!",
                delete_after=5,
            )
        if author.id in self.in_progress_users:
            return await ctx.send(
                "You can't start a new ticket. You're already in the middle of creating one!",
                delete_after=5,
            )

        modmail_setup_guilds: List[discord.Guild] = [
            guild
            for guild in author.mutual_guilds
            if self.client.get_modmail_channel(guild.id)
        ]

        if len(modmail_setup_guilds) == 0:
            await ctx.send(
                "You are not in a server which has activated the modmail feature"
            )
            return

        self.in_progress_users.add(author.id)
        embed = PaginatedEmbed(
            title="Anonymous Modmail Ticket System",
            description=(
                "You have triggered the anonymous modmail ticket system.\n"
                "When activated, you can have a conversation with a selected server's moderators anonymously.\n"
                f"Please select a server by reacting with the associated number emoji or cancel with {AnonymousModmail.cancel_emoji}."
            ),
            options=[
                (guild.name, f"Server ID: {guild.id}") for guild in modmail_setup_guilds
            ],
        )

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                user == author
                and reaction.message.id == message.id
                and str(reaction)
                in {AnonymousModmail.confirm_emoji, AnonymousModmail.cancel_emoji}
            )

        try:
            cancel_message: str = "Request successfully cancelled. No messages will be sent to the mods."
            option_index: Optional[int] = await embed.send(ctx, author, self.client)
            if option_index is None:
                return await ctx.send(cancel_message)

            selected_guild: discord.Guild = modmail_setup_guilds[option_index]
            embed = discord.Embed(
                title="Anonymous Modmail Confirmation",
                description=(
                    "Confirm that you want to speak to the moderators of "
                    f"**{selected_guild.name}** (Server ID: {selected_guild.id}) "
                    f"by reacting with a {AnonymousModmail.confirm_emoji}. Cancel with {AnonymousModmail.cancel_emoji}"
                ),
            )
            message: discord.Message = await ctx.send(embed=embed)
            await message.add_reaction(AnonymousModmail.confirm_emoji)
            await message.add_reaction(AnonymousModmail.cancel_emoji)

            reaction, _ = await self.client.wait_for(
                "reaction_add", timeout=60.0, check=check
            )
            emoji: str = reaction.emoji
            if emoji == AnonymousModmail.cancel_emoji:
                self.in_progress_users.remove(author.id)
                return await ctx.send(cancel_message)

            random_ticket_name: str = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
            modmail_category: discord.CategoryChannel = self.client.get_modmail_channel(
                selected_guild.id
            )
            # TODO: Get rid of this hardcoded role
            moderator_role: discord.Role = discord.utils.get(
                selected_guild.roles, name="Moderator"
            )
            ticket_channel: discord.TextChannel = await selected_guild.create_text_channel(
                f"ticket-{random_ticket_name}",
                category=modmail_category,
                overwrites={
                    selected_guild.default_role: discord.PermissionOverwrite(
                        read_messages=False
                    ),
                    moderator_role: discord.PermissionOverwrite(read_messages=True),
                },
                reason="Anonymous Modmail Ticket",
            )
            self.user_to_channel[author.id] = ticket_channel
            self.channel_to_user[ticket_channel.id] = author
            embed = discord.Embed(
                title="New Ticket",
                description=f"You can always close the ticket using `{self.client.command_prefix}close`",
                timestamp=discord.utils.utcnow(),
                color=discord.Color.green(),
            )
            await ticket_channel.send(embed=embed)
            await ctx.send(
                "You have confirmed. Send a message to start the conversation.\n"
                f"If there is not a {AnonymousModmail.confirm_emoji} on a message you send, please try again or open a new ticket.\n"
                "If you do not hear back within 24 hours, please open a new ticket."
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
                await message.add_reaction(AnonymousModmail.confirm_emoji)
        else:
            if self.user_to_channel.get(message.author.id):
                await self.on_user_message(message)
                await message.add_reaction(AnonymousModmail.confirm_emoji)

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
        await ticket_channel.send(f"__Anonymous User:__ {message.content}", files=files)

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
            timestamp=discord.utils.utcnow(),
            color=discord.Color.red(),
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


async def setup(client):
    await client.add_cog(AnonymousModmail(client))
