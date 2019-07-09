import discord
from discord.ext import commands
import asyncio

COURSE_REGISTRATION_CHANNEL_ID = 485279507582943262


class CourseRegistration(commands.Cog):
    def __init__(self, client):
        self.client = client
        # flag to determine whether all non-admin messages should be deleted or not on send
        self.deleteMessages = True

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        channel = message.channel
        # if author exists (message not a webhook) & user has an administrator permissions
        admin = author.permissions_in(channel).administrator if author else False
        # AutoDelete Non-Admin Messages in #course-registration if flag is set
        if channel.id == COURSE_REGISTRATION_CHANNEL_ID:
            # if user is not an admin or HuskyBot
            if (not admin and author != self.client.user):
                await asyncio.sleep(5)
                await message.delete()
            else:
                # if flag is set to True and the user is HuskyBot
                if self.deleteMessages and author == self.client.user:
                    await asyncio.sleep(5)
                    await message.delete()

    # toggles #course-registration auto-deletion
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def toggleAD(self, ctx):
        self.deleteMessages = not self.deleteMessages
        await ctx.send(f"Auto-deletion was toggled to: {self.deleteMessages}")

    # removes all course roles from every member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newSemester(self, ctx):
        await ctx.send("Goodbye courses...")
        for member in ctx.guild.members:
            rolesToRemove = list(filter(lambda r: '-' in r.name, member.roles))
            await member.remove_roles(*rolesToRemove)
        await ctx.send("No classes! WOO!")

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

    # removes all course roles from every member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def updateCategories(self, ctx):
        try:
            BLACKLISTED_CATEGORIES = ['ADMINS', 'INFO', 'DISCUSSION', 'MEDIA']
            NOT_REGISTERED_ROLE = discord.utils.get(ctx.guild.roles, name="Not Registered")
            for category in ctx.guild.categories:
                if category.name not in BLACKLISTED_CATEGORIES:
                    await category.set_permissions(NOT_REGISTERED_ROLE, read_messages=False)
            await ctx.send("Done!")
        except Exception as e:
            print(e)

    # sends a new embedded msg with the given title and image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newEmbed(self, ctx, *args):
        await ctx.message.delete()
        title = ""
        url = ""
        for word in args:
            if "http" in word:
                url += word
            else:
                title += word.strip() + ' '
        embed = discord.Embed(
            title=title,
            colour=discord.Color.from_rgb(52, 54, 59)
        )
        try:
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            await ctx.send(":regional_indicator_a: -> SampleCourse-2000")
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
    async def editTitle(self, ctx, message: discord.Message, *args):
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


def setup(client):
    client.add_cog(CourseRegistration(client))
