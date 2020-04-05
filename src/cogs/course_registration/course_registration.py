import discord
from discord.ext import commands
from typing import List, Dict

from data.ids import COURSE_REGISTRATION_CHANNEL_ID


class CourseRegistration(commands.Cog):
    def __init__(self, client):
        self.client = client

    # removes all course roles from every member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newSemester(self, ctx):
        # remove course roles from every member
        async with ctx.channel.typing():
            await ctx.send("Goodbye courses...")
            for member in ctx.guild.members:
                rolesToRemove = list(filter(lambda r: '-' in r.name, member.roles))
                await member.remove_roles(*rolesToRemove, atomic=False)
            await ctx.send("Removed everyone's classes! WOO!")

        # reset reaction roles from every course message
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        async with COURSE_REGISTRATION_CHANNEL.typing():
            await ctx.send(f"Starting to clear up {COURSE_REGISTRATION_CHANNEL.mention}...")
            async for message in COURSE_REGISTRATION_CHANNEL.history(limit=None):
                if message.embeds and 'Add/Remove' in message.embeds[0].title:
                    reaction_cog: commands.Cog = self.client.get_cog('Reaction')
                    # remove all the reaction roles from the message
                    await reaction_cog.removeallrr.callback(reaction_cog, ctx, message.id)
                    # remove all the reactions from the message
                    await message.clear_reactions()
            await ctx.send(f"Finished reseting all reaction roles in {COURSE_REGISTRATION_CHANNEL.mention}!")

    # removes all course roles from every member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearCourses(self, ctx, member: discord.Member):
        await ctx.send(f"Clearing course roles for {member.name}...")
        rolesToRemove = list(filter(lambda r: '-' in r.name, member.roles))
        await member.remove_roles(*rolesToRemove, atomic=False)
        await ctx.send(f"Done removing all roles for {member.name}!")

    # removes all reactions from the given member in the course registration channel
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearReactions(self, ctx, member: discord.Member):
        COURSE_REGISTRATION_CHANNEL = self.client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        await ctx.send(f"Clearing reactions for {member.name} in {COURSE_REGISTRATION_CHANNEL.mention}...")
        async for message in COURSE_REGISTRATION_CHANNEL.history(limit=None):
            for reaction in message.reactions:
                await reaction.remove(member)
        await ctx.send(f"Done removing all reactions for {member.name}!")


def setup(client):
    client.add_cog(CourseRegistration(client))
