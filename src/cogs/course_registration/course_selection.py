import discord
import re
from discord.ext import commands

from checks import is_admin, in_channel
from data.ids import COURSE_REGISTRATION_CHANNEL_ID, ADMIN_CHANNEL_ID


class CourseSelection(commands.Cog):
    """Handles the interaction surrounding selecting courses or other roles
    from course-regisration via commands and clean-up.

    Attributes
    ------------
    delete_self_message: `bool`
        Flag to determine whether to delete message sent by itself in the
        course-registration channel or not.
    """

    def __init__(self, client):
        self.client = client
        self.delete_self_message: bool = True

    # returns a lower-case string without dashes and stripping whitespace
    def ignoreDashCase(self, input):
        return ' '.join(input.split('-')).lower().strip()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Deletes any message sent within 5 seconds in the course-registration channel.
        Will delete messages sent by itself when the delete_self_message flag is True,
        else it will not.

        Parameters
        -----------
        message: `discord.Message`
            The sent message.
        """
        channel: discord.TextChannel = message.channel
        if channel.id == COURSE_REGISTRATION_CHANNEL_ID:
            author: discord.Member = message.author
            admin: bool = author.permissions_in(channel).administrator
            if self.delete_self_message and author == self.client.user:
                await message.delete(delay=5)
            elif not admin and author != self.client.user:
                await message.delete(delay=5)

    @is_admin()
    @commands.command()
    async def toggleAD(self, ctx: commands.Context) -> None:
        """Toggles the delete_self_message flag."""
        self.delete_self_message = not self.delete_self_message
        await ctx.send(f"Deleting self-messages was toggled to: {self.delete_self_message}")

    # toggles course registration roles
    @commands.command()
    @commands.check_any(in_channel(COURSE_REGISTRATION_CHANNEL_ID), is_admin())
    async def choose(self, ctx, *args):
        message = ctx.message
        guild = ctx.guild
        member = message.author
        ADMIN_CHANNEL = self.client.get_channel(ADMIN_CHANNEL_ID)
        admin = member.permissions_in(ctx.channel).administrator
        args = ' '.join(args).strip()
        role = None
        await message.delete()  # deletes command
        # tries to find a role given the user input
        try:
            role = await commands.RoleConverter().convert(ctx, args)
        # if a role could not be found
        except discord.ext.commands.errors.BadArgument as e:
            for r in guild.roles:
                # if the given input is the same as a role when lowercase or/and ignoring dashes
                if (args.lower() == r.name.lower() or
                   self.ignoreDashCase(args) == self.ignoreDashCase(r.name)):
                    role = r
                    break
            # if no role exists
            if role is None:
                await ctx.send(e, delete_after=5)  # sends an error message to user about missing role
                pattern = re.compile(r'^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$')  # regex pattern for courses
                # if the given argument is the format of a course with dashes subbed in for spaces or normally
                if pattern.match(args.upper()) or pattern.match(args.replace(' ', '-').upper()):
                    # notify the admins and tell the user about this notification.
                    await ADMIN_CHANNEL.send(f"{member.mention} just tried to add `{args}` using the `.choose` command. Consider adding this course.")
                    await ctx.send(f"The course `{args}` is not available but I have notified the admin team to add it.", delete_after=5)
                return
        # roles that a normal user is allowed to add other than course roles
        WHITELISTED_COLLEGES = ['CCIS', 'COE', 'BCHS', 'CAMD', 'DMSB', 'COS', 'CSSH', 'NUSL', 'EXPLORE']
        WHITELISTED_COLORS = ['ORANGE', 'LIGHT GREEN', 'YELLOW', 'PURPLE', 'LIGHT BLUE', 'PINK', 'LIGHT PINK', 'PALE PINK', 'CYAN', 'SPRING GREEN', 'PALE YELLOW', 'NAVY BLUE', 'LAVENDER']
        # if the role is one of the whitelisted roles or the user is an admin
        if ('-' in role.name or role.name in WHITELISTED_COLLEGES + WHITELISTED_COLORS or admin):
            # try to add or a remove a role to/from a user
            try:
                # if the role is already one of the user's role
                if (role in member.roles):
                    # remove the role from the user
                    await member.remove_roles(role)
                    await ctx.send(f"`{role.name}` has been removed.", delete_after=5)
                else:
                    # add the role to the user
                    await member.add_roles(role)
                    await ctx.send(f"`{role.name}` has been added!", delete_after=5)
            # in case of insufficient bot permissions
            except discord.errors.Forbidden:
                await ctx.send("I do not have permission to alter that role", delete_after=5)
        # if the role is not one of the whitelisted courses members are allowed to add.
        else:
            await ctx.send("You do not have the permission to toggle that role 🙃", delete_after=5)


def setup(client):
    client.add_cog(CourseSelection(client))
