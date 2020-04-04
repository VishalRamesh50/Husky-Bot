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

    # sends a new embedded msg with the given title and image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newEmbed(self, ctx, *args):
        await ctx.message.delete()
        args = ' '.join(args)
        if ',' not in args:
            await ctx.send("Use a comma to separate the title and image url")
            return
        args = args.split(',')
        title = args[0].strip()
        url = args[1].strip()
        if title == "" or url == "":
            await ctx.send("Title and url must have content")
            return
        embed = discord.Embed(
            title=title,
            colour=discord.Color.from_rgb(52, 54, 59)
        )
        try:
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            await ctx.send(":regional_indicator_a: -> Course Description (SampleCourse XXXX)")
        except discord.errors.HTTPException:
            await ctx.send(f"Not a valid image url")

    # edits the images for all the embedded messages in the given msg to the given image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editEmbedImage(self, ctx, message: discord.Message, url):
        await ctx.message.delete()
        for embed in message.embeds:
            try:
                embed.set_image(url=url)
                await message.edit(embed=embed)
                await ctx.send(f"Image for `{embed.title}` was edited")
            except discord.errors.HTTPException:
                await ctx.send("Not a valid image url")

    # edits the title for all the embedded messages in the given msg to the given title
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editEmbedTitle(self, ctx, message: discord.Message, *args):
        await ctx.message.delete()
        title = ' '.join(args)
        for embed in message.embeds:
            embed.title = title
            await message.edit(embed=embed)
            await ctx.send(f"Title for message `{message.id}` was edited")

    # edits the content of the message use '\n' to indicate newline
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editCourseContent(self, ctx, message: discord.Message, *args):
        await ctx.message.delete()
        if message.embeds == []:
            args = ' '.join(args).split("\\n")
            content = []
            for arg in args:
                content.append(arg.strip())
            content = '\n'.join(content)
            await message.edit(content=content)
            await ctx.send(f"Content for message `{message.id}` was edited")
        else:
            await ctx.send("You accidentally tried to edit the embedded message", delete_after=5)

    # sends a new embedded msg with the given title and image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def navEmbed(self, ctx):
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        # get all the messages in course-registration
        messages: List[discord.Message] = await COURSE_REGISTRATION_CHANNEL.history(limit=None).flatten()
        # filter out all the messages which don't have embeds or a title
        messages = list(filter(lambda x: x.embeds and x.embeds[0].title, messages))
        # sort the messages by their embed's title
        messages.sort(key=lambda m: (m.embeds[0].title))
        letter_to_link: Dict[str, str] = {}
        # assign a letter to the first jump_link of a message
        for message in messages:
            course: str = message.embeds[0].title.replace('Add/Remove ', '')
            starting_letter: str = course[0]
            # if the course starting with the letter has not been added yet
            if letter_to_link.get(starting_letter) is None:
                letter_to_link[starting_letter] = message.jump_url

        alpha_links: str = ""
        # Each letter has it's own thing
        for letter, link in letter_to_link.items():
            alpha_links += f"[{letter}]({link}) **|** "

        # remove the trailing divider
        alpha_links = alpha_links[:-7]
        try:
            embed = discord.Embed(
                title="Quick Links!",
                description=f"Jump to each course category starting with the given letter by simply clicking on the links below\n{alpha_links}",
                colour=discord.Colour.red()
            )
        # if there are too many characters in the description
        except 400 as e:
            print(type(e))
            print(e)
            embed = discord.Embed(
                title="Quick Links!",
                description=f"Jump to each course category starting with the given letter by simply clicking on the links below",
                colour=discord.Colour.red()
            )
            # Divide by the middle for 2 groups
            # 7 links is about the most a field can hold
            middle: int = min(len(letter_to_link) // 2, 7)
            counter: int = 0
            for key, val in letter_to_link.items():
                alpha_links += f"[{key}]({val}) "
                counter += 1
                if counter % middle == 0 or counter == len(letter_to_link):
                    embed.add_field(name=f"{alpha_links[1]}-{key}", value=alpha_links, inline=True)

        top_messages: List[discord.Message] = await COURSE_REGISTRATION_CHANNEL.history(limit=4, oldest_first=True).flatten()
        embed.add_field(name=f"Top Of Page", value=f"[Pick School/Major Here]({top_messages[0].jump_url})", inline=True)
        embed.add_field(name=f"Colors", value=f"[Choose Colors Here]({top_messages[2].jump_url})", inline=True)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(CourseRegistration(client))
