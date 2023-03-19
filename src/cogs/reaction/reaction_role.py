import discord
import random
import string
from discord.ext import commands
from typing import Optional

from client.bot import Bot
from checks import is_admin


class ReactionRole(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        """Adds the role associated with a reaction role if one exists
        when a member adds a reaction to a message.

        Parameters
        -------------
        payload: `discord.RawReactionActionEvent`
            The reaction payload with information about the event.
        """

        member: Optional[discord.Member] = payload.member
        if not (payload.guild_id and member) or member.bot:
            return

        guild: discord.Guild = self.client.get_guild(payload.guild_id)

        specs = {
            "server_id": guild.id,
            "message_id": payload.message_id,
            "reaction": payload.emoji.name,
        }
        result: Optional[dict] = self.client.db.find_one_reaction_role(specs)
        if result:
            role_object: discord.Role = guild.get_role(result["role_id"])
            await member.add_roles(role_object)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        """Removes the role associated with a reaction role if one exists
        when a member removes a reaction from a message.

        Parameters
        ------------
        payload: `discord.RawReactionActionEvent`
            The reaction payload with information about the event.
        """

        if payload.guild_id is None:
            return
        guild: discord.Guild = self.client.get_guild(payload.guild_id)
        member: Optional[discord.Member] = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        specs = {
            "server_id": guild.id,
            "message_id": payload.message_id,
            "reaction": payload.emoji.name,
        }
        result: Optional[dict] = self.client.db.find_one_reaction_role(specs)
        if result:
            role_object: discord.Role = guild.get_role(result["role_id"])
            await member.remove_roles(role_object)

    @is_admin()
    @commands.guild_only()
    @commands.command()
    async def newrr(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        message_id: int,
        reaction: str,
        role: discord.Role,
    ) -> None:
        """Creates a new reaction role if one does not already exist.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        channel: `discord.TextChannel`
            The channel which to add the reaction role in.
        message_id: `int`
            The message id of the message to add a reaction role to.
        reaction: `discord.Emoji`
            The emoji which the reaction role will be associated with.
        role: `discord.Role`
            The role which the reaction role will be associated with.
        """

        alphabet: str = string.ascii_letters + string.digits + "-_"
        while True:
            key: str = "".join(random.choice(alphabet) for i in range(9))
            if not self.client.db.reaction_role_exists({"key": key}):
                break

        try:
            message: discord.Message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Given message could not be retreived")
            return

        try:
            await message.add_reaction(reaction)
        except discord.Forbidden:
            await ctx.send("This message already has the maximum number of reactions.")
            return
        except (discord.HTTPException, discord.NotFound, TypeError):
            await ctx.send(f'"{reaction}" is not a valid emoij.')
            return

        data = {
            "server_id": ctx.guild.id,
            "message_id": message_id,
            "channel_id": channel.id,
            "reaction": reaction,
            "role_id": role.id,
        }
        if not self.client.db.reaction_role_exists(data):
            self.client.db.create_reaction_role({**data, "key": key})
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(
                name="New Reaction Role Set!", icon_url=self.client.user.avatar_url
            )
            embed.set_thumbnail(url=self.client.user.avatar_url)
            embed.add_field(name="🔑 Key", value=key, inline=False)
            embed.add_field(name="📺 Channel", value=channel.mention, inline=False)
            embed.add_field(name="💬 Message", value=message_id, inline=False)
            embed.add_field(name="🎨 Reaction", value=reaction, inline=False)
            embed.add_field(name="🏷 Role", value=role.mention, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("This reaction role already exists.")

    @newrr.error
    async def newrr_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Error handler for newrr command.
        If valid argument were not given, send feedback to user.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        error `commands.CommandError`:
            The error which was raised.
        """

        if isinstance(error, commands.BadArgument):
            if isinstance(error.__cause__, ValueError):
                await ctx.send(
                    f"`message_id: {ctx.args.message_id}` is not a valid integer."
                )
            else:
                await ctx.send(str(error))
            ctx.command_failed = False

    @is_admin()
    @commands.guild_only()
    @commands.command()
    async def fetchrr(self, ctx: commands.Context, given_message_id: str) -> None:
        """Fetches all the reactions, roles, keys for a given message_id.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        given_message_id: `str`
            A message id as a string.
        """

        guild: discord.Guild = ctx.guild
        try:
            message_id: int = int(given_message_id)
        except ValueError:
            await ctx.send("The given message_id must be an integer.")
            return

        options = {"server_id": guild.id, "message_id": message_id}
        if self.client.db.reaction_role_exists(options):
            embed = embed = discord.Embed(
                description=(f"Message ID: `{message_id}`"), color=discord.Color.red()
            )
            embed.set_author(
                name="Keys and Reactions!", icon_url=self.client.user.avatar_url
            )
            for doc in self.client.db.find_reaction_roles(options):
                key: str = doc["key"]
                reaction: str = doc["reaction"]
                role: str = guild.get_role(doc["role_id"]).mention
                embed.add_field(name=f"`{key}`", value=f"<{reaction}>\n{role}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                f"There are no reaction roles set for message: `{message_id}`"
            )

    @is_admin()
    @commands.guild_only()
    @commands.command()
    async def removerr(self, ctx: commands.Context, key: str) -> None:
        """Removes a reaction role from a message tied to the given key.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        key: `str`
            A key to search for a specific reaction role.
        """

        result: Optional[dict] = self.client.db.find_one_reaction_role({"key": key})
        if result:
            channel: discord.TextChannel = self.client.get_channel(result["channel_id"])
            message: discord.Message = await channel.fetch_message(result["message_id"])
            await message.remove_reaction(result["reaction"], self.client.user)
            self.client.db.remove_reaction_role(key)
            await ctx.send(f"Removed reaction role of key `{key}`")
        else:
            await ctx.send("There are no reaction roles with the given key")

    @is_admin()
    @commands.guild_only()
    @commands.command()
    async def removeallrr(self, ctx: commands.Context, given_message_id: str):
        """Removes all reaction roles from the given message.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        given_message_id: `str`
            A message id as a string.
        """

        try:
            message_id = int(given_message_id)
        except ValueError:
            await ctx.send("The given message_id must be an integer.")
            return

        options = {"server_id": ctx.guild.id, "message_id": message_id}
        if self.client.db.reaction_role_exists(options):
            for doc in self.client.db.find_reaction_roles(options):
                channel_object = self.client.get_channel(doc["channel_id"])
                message_object = await channel_object.fetch_message(message_id)
                await message_object.remove_reaction(doc["reaction"], self.client.user)
                self.client.db.remove_reaction_role(doc["key"])
            await ctx.send(f"Removed all reaction roles from message: `{message_id}`")
        else:
            await ctx.send("There are no reaction roles for the given message.")


async def setup(client):
    await client.add_cog(ReactionRole(client))
