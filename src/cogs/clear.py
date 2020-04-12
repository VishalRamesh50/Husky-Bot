import discord
from discord.ext import commands
from typing import List

from checks import is_admin, is_mod


class Clear(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.MESSAGE_DELETE_CAPACITY = 500
        self.MEMBER_DELETE_CAPACITY = 100

    @commands.command()
    @commands.guild_only()
    @commands.check_any(is_admin(), is_mod())
    async def clear(
        self, ctx: commands.Context, amount: int = 1, member: discord.Member = None
    ) -> None:
        """Deletes a set amount of message from the current channel.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        amount: `int`
            The amount of message to delete from the current channel.
        member: `discord.Member`
            Will delete messages only from the given member.
        """

        channel = ctx.channel
        await ctx.message.delete()

        if amount <= 0:
            await ctx.send("Cannot delete less than 1 message.")
            return

        deleted_messages: List[discord.Message] = []
        if member is None:
            if amount > self.MESSAGE_DELETE_CAPACITY:
                await ctx.send(
                    f"Cannot delete more than {self.MESSAGE_DELETE_CAPACITY} "
                    "messages at a time."
                )
                return
            deleted_messages = await channel.purge(limit=amount)
        else:
            if amount > self.MEMBER_DELETE_CAPACITY:
                await ctx.send(
                    f"Cannot delete more than {self.MEMBER_DELETE_CAPACITY} "
                    "messages when a member is mentioned."
                )
                return
            num_deleted: int = 0
            async for message in channel.history(limit=None):
                if num_deleted == amount:
                    break
                if message.author == member:
                    deleted_messages.append(message)
                    num_deleted += 1
            await channel.delete_messages(deleted_messages)
        await ctx.send(f"{len(deleted_messages)} messages deleted.", delete_after=5)


def setup(client):
    client.add_cog(Clear(client))
