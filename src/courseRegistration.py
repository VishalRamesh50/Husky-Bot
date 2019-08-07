import discord
from discord.ext import commands
import asyncio

COURSE_REGISTRATION_CHANNEL_ID = 485279507582943262


class CourseRegistration(commands.Cog):
    def __init__(self, client):
        self.client = client
        # flag to determine whether all non-admin messages should be deleted or not on send
        self.deleteMessages = True

    # if the message was sent in the COURSE_REGISTRATION_CHANNEL or the author is an admin
    def inCourseRegistration(ctx):
        # if user has an administrator permissions
        admin = ctx.author.permissions_in(ctx.channel).administrator
        return ctx.channel.id == COURSE_REGISTRATION_CHANNEL_ID or admin

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        channel = message.channel
        # if message not a webhook & user has an administrator permissions
        admin = message.webhook_id is None and author.permissions_in(channel).administrator
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

    # toggles course registration roles
    @commands.command()
    @commands.check(inCourseRegistration)
    async def choose(self, ctx, *args):
        message = ctx.message
        guild = ctx.guild
        member = message.author
        admin = member.permissions_in(ctx.channel).administrator
        await message.delete()
        args = ' '.join(args).strip()
        role = None
        try:
            role = await commands.RoleConverter().convert(ctx, args)
        except discord.ext.commands.errors.BadArgument as e:
            for r in guild.roles:
                if (args.lower() == r.name.lower() or
                   self.ignoreDashCase(args) == self.ignoreDashCase(r.name)):
                    role = r
                    break
            if role is None:
                await ctx.send(e, delete_after=5)
                return
        WHITELISTED_COLLEGES = ['CCIS', 'COE', 'BCHS', 'CAMD', 'DMSB', 'COS', 'CSSH', 'EXPLORE']
        WHITELISTED_COLORS = ['ORANGE', 'LIGHT GREEN', 'YELLOW', 'PURPLE', 'LIGHT BLUE', 'PINK', 'LIGHT PINK', 'PALE PINK', 'CYAN', 'SPRING GREEN', 'PALE YELLOW']
        if ('-' in role.name or role.name in WHITELISTED_COLLEGES + WHITELISTED_COLORS or admin):
            if (role in member.roles):
                try:
                    await member.remove_roles(role)
                    await ctx.send(f"{role.name} has been removed", delete_after=5)
                except discord.errors.Forbidden:
                    await ctx.send("I do not have permission to alter that role", delete_after=5)
            else:
                try:
                    await member.add_roles(role)
                    await ctx.send(f"{role.name} has been added!", delete_after=5)
                except discord.errors.Forbidden:
                    await ctx.send("I do not have permission to alter that role", delete_after=5)
        else:
            await ctx.send("You do not have the permission to toggle that role 🙃", delete_after=5)

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