import asyncio
import discord
from datetime import datetime
from discord.ext import commands
from data.ids import GUILD_ID, MOD_CATEGORY_ID
from typing import Dict


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
    ticket_count: `int`
        The total number of tickets created since the bot started up.
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_to_channel: Dict[int, discord.TextChannel] = {}
        self.channel_to_user: Dict[int, discord.User] = {}
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
        author: discord.User = ctx.author

        if self.user_to_channel.get(author.id):
            await ctx.send(
                "You can't start a new ticket. You're already in the middle of one!",
                delete_after=5,
            )
            return

        embed = discord.Embed(
            title="Anonymous Modmail Ticket System",
            description=(
                "You have triggered the anonymous modmail ticket system.\n"
                "When activated, you can have a conversation with the NU mods anonymously.\n"
                "Confirm by reacting with a ✅. Cancel with ❌"
            ),
        )
        confirmation_msg: discord.Message = await ctx.send(embed=embed)
        await confirmation_msg.add_reaction("✅")
        await confirmation_msg.add_reaction("❌")

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
                guild: discord.Guild = self.client.get_guild(GUILD_ID)
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
                await ctx.send(
                    "Request successfully cancelled. No messages will be sent to the mods."
                )
        except asyncio.TimeoutError:
            await ctx.send("No confirmation received. Cancelled.")

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
        await ticket_user.send(f"{message.author.name}: {message.content}", files=files)

    async def on_user_message(self, message: discord.Message) -> None:
        """Sends a message to the mods anonymously.

        Parameters
        -------------
        message: `discord.Message`
            The message sent by the ticket user to be sent to the mods.
        """
        ticket_channel: discord.TextChannel = self.user_to_channel[message.author.id]
        files: List[discord.File] = [await a.to_file() for a in message.attachments]
        await ticket_channel.send(f"Anonymous User: {message.content}", files=files)


def setup(client):
    client.add_cog(AnonymousModmail(client))
