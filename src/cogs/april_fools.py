import asyncio
import discord
import logging
from discord.ext import commands, tasks
from random import randint
from typing import Optional

from checks import is_admin
from data.ids import GUILD_ID, NOT_REGISTERED_ROLE_ID

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AprilFools(commands.Cog):
    """This controls the logic related to
    the April Fools event.

    Attributes
    -------------
    client: `commands.Bot`
        The instance of the client connection to Discord.
    paused: `bool`
        A flag indicating if the infection should be paused or not.
    sender_rate: `int`
        The denominator by which the calculation for infection rate is performed
        every time a user sends a message in a channel.
    sender_rate: `int`
        The denominator by which the calculation for infection rate is performed
        every time a user is sent a message in a channel.
    merge_rate: `int`
        The rate at which channels are deleted and their members are merged into others
        in terms of minutes.
    last_quarantine_channel_num: `int`
        The number of the last quarantine channel to delete and then merge.
    notify: `bool`
        A flag indicating whether users should be notified when they've been infected or not.
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.paused: bool = False
        self.sender_rate: int = 200
        self.listener_rate: int = self.sender_rate * 10
        self.merge_rate: int = 20
        self.notify: bool = False

    @property
    def infected_count(self) -> int:
        guild: discord.Guild = self.client.get_guild(GUILD_ID)
        INFECTED_ROLE: discord.Role = discord.utils.get(guild.roles, name="Infected")
        return len(list(filter(lambda m: INFECTED_ROLE in m.roles, guild.members)))

    @property
    def last_quarantine_channel_num(self) -> int:
        guild: discord.Guild = self.client.get_guild(GUILD_ID)
        quarantine_category: discord.CategoryChannel = discord.utils.get(
            guild.categories, name="QUARANTINE"
        )
        last_quarantine_channel: discord.TextChannel = quarantine_category.text_channels[
            -1
        ]
        return int(last_quarantine_channel.name.split("-")[1])

    @is_admin()
    @commands.command(aliases=["initAF"])
    async def init_af(self, ctx: commands.Context) -> None:
        logger.debug("April fools being initialized...")
        guild: discord.Guild = ctx.guild

        # make all channel hidden for normal users
        logger.debug("About to hide all channels for normal users...")
        category_names = ["INFO", "DISCUSSION", "ASSORTED", "MEDIA"]
        for name in category_names:
            curr_category: discord.CategoryChannel = discord.utils.get(
                guild.categories, name=name
            )
            for c in curr_category.text_channels:
                await c.set_permissions(guild.default_role, read_messages=False)

        # make new category
        logger.debug("About to make new category...")
        MODERATOR_ROLE: discord.Role = discord.utils.get(guild.roles, name="Moderator")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            MODERATOR_ROLE: discord.PermissionOverwrite(read_messages=True),
        }
        category: discord.CategoryChannel = await guild.create_category(
            "QUARANTINE", overwrites=overwrites
        )
        await ctx.send(f"Created {category.name} category...")

        logger.debug("Filtering out Not Registered Members...")
        NOT_REGISTERED_ROLE: discord.Role = guild.get_role(NOT_REGISTERED_ROLE_ID)
        registered_members = filter(
            lambda m: NOT_REGISTERED_ROLE not in m.roles and not m.bot, guild.members
        )
        logger.debug("Creating the groups...")
        channel_count: int = 0
        member_count: int = 0
        INFECTED_ROLE: discord.Role = discord.utils.get(guild.roles, name="Infected")
        for member in registered_members:
            if randint(0, 50) == 0:
                logger.debug(f"{member.name} was randomly infected as a Patient 0")
                await member.add_roles(INFECTED_ROLE, reason="Patient 0")
            if member_count % 20 == 0:
                logger.debug("============================")
                channel_name: str = f"quarantine-{channel_count}"
                channel: discord.TextChannel = await category.create_text_channel(
                    channel_name, overwrites=overwrites
                )
                channel_count += 1
            await channel.set_permissions(
                member, read_messages=True, send_messages=True
            )
            logger.debug(f"{channel_name}: {member.name} ({member_count})")
            member_count += 1

        await ctx.send(f"Created {self.last_quarantine_channel_num + 1} groups...")
        logger.debug(f"Created {self.last_quarantine_channel_num + 1} groups...")
        await ctx.send("April Fools has started!")
        logger.debug(f"Sucessfully initialized April Fools Module!")
        await self.merge_channel_loop.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if self.paused:
            return

        guild: Optional[discord.Guild] = message.guild
        if guild is None:
            return

        channel: discord.TextChannel = message.channel
        if "quarantine" not in channel.name:
            return

        INFECTED_ROLE: discord.Role = discord.utils.get(guild.roles, name="Infected")
        infected_count_in_channel: int = len(
            list(filter(lambda m: INFECTED_ROLE in m.roles, channel.members))
        )
        sender: discord.Member = message.author

        if infected_count_in_channel > 0:
            sender_max: int = int(max(self.sender_rate / infected_count_in_channel, 3))
            if randint(0, sender_max) == 0:
                logger.debug("A sender was infected")
                await sender.add_roles(INFECTED_ROLE, reason="Got infected!")
                if self.notify:
                    await channel.send(f"Oh no! {sender} got infected!")

            listener_max: int = int(
                max(self.listener_rate / infected_count_in_channel, 3)
            )
            for member in channel.members:
                if member != sender:
                    if randint(0, listener_max) == 0:
                        logger.debug("A listener was infected")
                        await member.add_roles(INFECTED_ROLE, reason="Got infected!")
                        if self.notify:
                            await channel.send(f"Oh no! {member} got infected!")

    @is_admin()
    @commands.command()
    async def change_sender_rate(self, ctx: commands.Context, sender_rate: int) -> None:
        logger.debug("Changing sender rate.")
        og_sender_rate: int = self.sender_rate
        og_listener_rate: int = self.listener_rate
        self.sender_rate = sender_rate
        self.listener_rate = self.sender_rate * 10
        await ctx.send(
            f"Sender rate changed from {og_sender_rate} to {self.sender_rate}"
        )
        await ctx.send(
            f"Listener rate changed from {og_listener_rate} to {self.listener_rate}"
        )

    @is_admin()
    @commands.command()
    async def change_listener_rate(
        self, ctx: commands.Context, listener_rate: int
    ) -> None:
        logger.debug("Changing listener rate.")
        await ctx.send(
            f"Listener rate changed from {self.listener_rate} to {listener_rate}"
        )
        self.listener_rate = listener_rate

    @is_admin()
    @commands.command()
    async def current_af_rate(self, ctx: commands.Context) -> None:
        logger.debug("Current AF rate was triggered.")
        await ctx.send(
            "The current rate is "
            f"{self.sender_rate} for senders and {self.listener_rate} for listeners."
        )

    @is_admin()
    @commands.command()
    async def get_infected_count(self, ctx: commands.Command) -> None:
        logger.debug("infected_count was called")
        await ctx.send(
            f"There are a total of {self.infected_count} members infected now."
        )

    @is_admin()
    @commands.command()
    async def get_merge_rate(self, ctx: commands.Command) -> None:
        logger.debug("Get merge rate was triggered.")
        await ctx.send(f"The current merge rate is {self.merge_rate}mins.")

    @is_admin()
    @commands.command(aliases=["toggleAF"])
    async def toggle_af(self, ctx: commands.Context) -> None:
        logger.debug("AF was toggled.")
        self.paused = not self.paused
        if self.paused:
            await ctx.send(
                f"April fools has been paused. Infections will not occur now."
            )
        else:
            await ctx.send(f"April fools has been unpaused.")
            await ctx.send(
                "Infections will continue at a rate of "
                f"{self.sender_rate} per sender and {self.listener_rate} per listener."
            )

    @is_admin()
    @commands.command()
    async def toggle_notify(self, ctx: commands.Command) -> None:
        logger.debug("Notify flag was toggled.")
        self.notify = not self.notify
        await ctx.send(f"Notify flag now set to {self.notify}")

    @is_admin()
    @commands.command()
    async def set_merge_rate(self, ctx: commands.Command, merge_rate: int) -> None:
        logger.debug("Set merge rate was triggered.")
        await ctx.send(f"Merge rate set from {self.merge_rate} to {merge_rate}mins.")
        self.merge_rate = merge_rate

    @is_admin()
    @commands.command()
    async def get_infected_members(self, ctx: commands.Command) -> None:
        logger.debug("get_infected was called.")
        guild: discord.Guild = ctx.guild
        INFECTED_ROLE: discord.Role = discord.utils.get(guild.roles, name="Infected")
        infected_members: str = ""
        for member in filter(lambda m: INFECTED_ROLE in m.roles, guild.roles):
            infected_members += member.name + " "
        await ctx.send(f"Infected members are: {infected_members}")

    @is_admin()
    @commands.command(aliases=["endAF"])
    async def end_af(self, ctx: commands.Context) -> None:
        logger.debug("Ending April fools...")
        guild: discord.Guild = ctx.guild
        category: discord.CategoryChannel = discord.utils.get(
            guild.categories, name="QUARANTINE"
        )
        for c in category.text_channels:
            await c.delete(reason="AF over")
        await category.delete(reason="AF over")

        category_names = ["INFO", "DISCUSSION", "ASSORTED", "MEDIA"]
        for name in category_names:
            curr_category: discord.CategoryChannel = discord.utils.get(
                guild.categories, name=name
            )
            for c in curr_category.text_channels:
                await c.set_permissions(guild.default_role, read_messages=True)

        general_channel: discord.CategoryChannel = discord.utils.get(
            guild.text_channels, name="general"
        )

        NOT_REGISTERED_ROLE: discord.Role = guild.get_role(NOT_REGISTERED_ROLE_ID)
        registered_members = filter(
            lambda m: NOT_REGISTERED_ROLE not in m.roles and not m.bot, guild.members
        )
        await general_channel.send(
            "Alright April Fools event is over! "
            f"There were {self.infected_count}/{len(list(registered_members))} infected members!"
            "Stay safe out there guys!"
        )
        self.paused = True

    async def merge_channel(self):
        guild: discord.Guild = self.client.get_guild(GUILD_ID)
        logger.debug("Merging channels now!")
        channel: discord.TextChannel = discord.utils.get(
            guild.text_channels, name=f"quarantine-{self.last_quarantine_channel_num}",
        )
        logger.debug("Adding members to random quarantine channel.")
        for member in channel:
            rand_channel: discord.TextChannel = discord.utils.get(
                guild.text_channels,
                name=f"quarantine-{randint(0, self.last_quarantine_channel_num - 1)}",
            )
            await rand_channel.set_permissions(
                member, read_messages=True, send_messages=True
            )
            await rand_channel.send(f"Please welcome your new member: {member.mention}")
        logger.debug(f"Deleting channel {channel.name}...")
        await channel.delete()

    @is_admin()
    @commands.command()
    async def merge_channel_manually(self, ctx: commands.Context) -> None:
        await self.merge_channel()

    @tasks.loop()
    async def merge_channel_loop(self):
        logger.debug("Merging channels loop initialized.")
        while not self.client.is_closed():
            await asyncio.sleep(self.merge_rate * 60)
            await self.merge_channel()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await member.send(
            "If you're wondering where all the channels are... "
            "We're in the middle of an April Fools event. "
            "Wait until April 2nd to see the server as normal."
        )


def setup(client):
    client.add_cog(AprilFools(client))
