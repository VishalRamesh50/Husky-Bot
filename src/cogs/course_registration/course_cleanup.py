import discord
from discord.ext import commands
from typing import List

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID


class CourseCleanup(commands.Cog):
    """Has some commands to handle mass removals of roles
    and/or reactions related to course registration.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @is_admin()
    @commands.guild_only()
    @commands.command()
    async def newSemester(self, ctx: commands.Context) -> None:
        """Removes all course roles from every member and removes all reaction roles
        for courses.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        guild: discord.Guild = ctx.guild
        async with ctx.channel.typing():
            await ctx.send("Goodbye courses...")
            for member in guild.members:
                roles_to_remove: List[discord.Role] = list(
                    filter(lambda r: "-" in r.name, member.roles)
                )
                await member.remove_roles(*roles_to_remove, atomic=False)
            await ctx.send("Removed everyone's classes! WOO!")

        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        async with COURSE_REGISTRATION_CHANNEL.typing():
            await ctx.send(
                f"Starting to clear up {COURSE_REGISTRATION_CHANNEL.mention}..."
            )
            async for message in COURSE_REGISTRATION_CHANNEL.history(limit=None):
                if message.embeds and "Add/Remove" in str(message.embeds[0].title):
                    removeallrr_command: commands.Command = self.client.get_command(
                        "removeallrr"
                    )
                    await ctx.invoke(removeallrr_command, message.id)
                    await message.clear_reactions()
            await ctx.send(
                f"Finished reseting all reaction roles in {COURSE_REGISTRATION_CHANNEL.mention}!"
            )

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["clearCourses"])
    async def clear_courses(
        self, ctx: commands.Context, member: discord.Member
    ) -> None:
        """Removes all course roles from a given member.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        member: `discord.Member`
            The member to remove all course roles from.
        """
        async with ctx.channel.typing():
            roles_to_remove: List[discord.Role] = list(
                filter(lambda r: "-" in r.name, member.roles)
            )
            await member.remove_roles(*roles_to_remove, atomic=False)
            await ctx.send(f"Done removing all roles for {member.name}!")

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["clearReactions"])
    async def clear_reactions(self, ctx, member: discord.Member):
        """Removes all reactions from the given member in the course registration channel.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        member: `discord.Member`
            The member to remove all reactions from.
        """
        guild: discord.Guild = ctx.guild
        COURSE_REGISTRATION_CHANNEL = guild.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        async with ctx.channel.typing():
            await ctx.send(
                f"Clearing reactions for {member.name} in {COURSE_REGISTRATION_CHANNEL.mention}..."
            )
            async for message in COURSE_REGISTRATION_CHANNEL.history(limit=None):
                for reaction in message.reactions:
                    await reaction.remove(member)
            await ctx.send(f"Done removing all reactions for {member.name}!")


def setup(client):
    client.add_cog(CourseCleanup(client))
