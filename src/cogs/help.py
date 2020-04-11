import discord
from discord.ext import commands
from typing import Union, Optional


class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.question_mark = "https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png"

    @property
    def avatar(self) -> str:
        return self.client.user.avatar_url

    def _get_embed(self, title: str) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=f"Help | {title}", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        return embed

    @commands.group()
    async def help(self, ctx: commands.Context) -> None:
        guild: Optional[discord.Guild] = ctx.guild
        if guild is None:
            await ctx.send("This must be invoked from a guild", delete_after=5)
            return

        author: discord.Member = ctx.author
        channel: discord.TextChannel = ctx.channel
        admin: bool = author.permissions_in(channel).administrator
        mod: Optional[discord.Role] = discord.utils.get(author.roles, name="Moderator")
        embed = discord.Embed(
            description=(
                "To see a page, just add the page number/name after the `.help` command.\n"
                "Like this: `.help 1` or `.help activity`"
            ),
            colour=discord.Colour.red(),
        )
        embed.set_author(name="Help", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        if admin or mod:
            embed.add_field(name="Aoun", value="How to use Aoun commands!")
            embed.add_field(name="Clear", value="How to use the clear command!")
        if admin:
            embed.add_field(
                name="Course Registration",
                value="How to use Course Registration commands!",
            )
            embed.add_field(name="Loader", value="How to use Loader commands!")
            embed.add_field(name="Reaction", value="How to use Reaction commands!")
            embed.add_field(name="Twitch", value="How to use Twitch commands!")

        embed.add_field(name="Page 1 | Activity", value="How to use activity commands!")
        embed.add_field(name="Page 2 | Day", value="How to use the day command!")
        embed.add_field(name="Page 3 | Hours", value="How to use the hours command!")
        embed.add_field(
            name="Page 4 | Ice Cream", value="How to use the icecream command!"
        )
        embed.add_field(
            name="Page 5 | Miscellaneous", value="How to use Miscellaneous commands!"
        )
        embed.add_field(name="Page 6 | Open", value="How to use the open command!")
        embed.add_field(
            name="Page 7 | Reminder", value="How to use the reminder command!"
        )
        embed.add_field(name="Page 8 | Stats", value="How to use Stats commands!")
        embed.add_field(
            name="Page 9 | Suggest", value="How to use the suggest command!"
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["Aoun"])
    async def aoun(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Aoun")
        embed.add_field(
            name="Commands",
            value="`.set_a_cooldown`, `.reset_a_cooldown`",
            inline=False,
        )
        embed.add_field(
            name=".set_a_cooldown", value="Sets a new Aoun cooldown", inline=False,
        )
        embed.add_field(
            name=".reset_a_cooldown", value="Resets the aoun cooldown", inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["setACooldown"])
    async def set_a_cooldown(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("set_a_cooldown")
        embed.add_field(
            name="Command", value="`.set_a_cooldown <cooldown>`", inline=False,
        )
        embed.add_field(
            name="Aliases", value="`.setACooldown", inline=False,
        )
        embed.add_field(
            name="Example", value="`.set_a_cooldown 30", inline=False,
        )
        embed.add_field(
            name="Note",
            value="Given cooldown is in seconds and must be less than 900",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Sets the cooldown rate between when aoun images should spawn "
                "when mentioned to avoid being spammed"
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["resetACooldown"])
    async def reset_a_cooldown(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("reset_a_cooldown")
        embed.add_field(
            name="Command", value="`.reset_a_cooldown", inline=False,
        )
        embed.add_field(
            name="Aliases", value="`.resetACooldown", inline=False,
        )
        embed.add_field(
            name="Example", value="`.reset_a_cooldown", inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=("Resets the cooldown rate back to the default (which is 5 seconds)"),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["Clear"])
    async def clear(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("clear")
        embed.add_field(
            name="Command", value="`.clear [number] [member]`", inline=False
        )
        embed.add_field(
            name="Example",
            value="`.clear` or `.clear 20` or `.clear 10 @member#1234`",
            inline=False,
        )
        embed.add_field(
            name="Note",
            value=(
                "If no number is given the last sent message is deleted"
                "Number must be greater than 0"
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Clears the last given number of messages in the channel or the ones specifically from a given member.",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["cr", "Course Registration"])
    async def course_registration(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Course Registration")
        embed.description = (
            "To see a page, just add the page name after the `.help` command.\n"
            "Like this: `.help create course`"
        )
        embed.add_field(
            name="Course Cleanup",
            value="Cleanup commands which automate bulk removals of course related things",
            inline=False,
        )
        embed.add_field(
            name="Course Content",
            value="Commands which help for creating/maintaining content essential to #course-registration",
            inline=False,
        )
        embed.add_field(
            name="Course Selection",
            value="Commands relating to the behavior of selecting courses via commands in #course-registration",
            inline=False,
        )
        embed.add_field(
            name="Create Course",
            value="Convenience commands which automate the process of creating a new course",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(
        aliases=["Course Cleanup", "course cleanup", "course-cleanup", "courseCleanup"]
    )
    async def course_cleanup(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self.get_embed("Course Cleanup")
        embed.add_field(
            name="Commands",
            value="`.new_semester`, `.clear_courses`, `.clear_reactions`",
            inline=False,
        )
        embed.add_field(
            name=".new_semester",
            value="Resets course roles and course reaction roles for new semester",
            inline=False,
        )
        embed.add_field(
            name=".clear_courses",
            value="Removes all course roles from a specific member",
            inline=False,
        )
        embed.add_field(
            name=".clear_reactions",
            value="Removes all course reactions for a specific member",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["newSemester"])
    async def new_semester(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self.get_embed("new_semester")
        embed.add_field(name="Command", value=".new_semester", inline=False)
        embed.add_field(name="Aliases", value=".newSemester", inline=False)
        embed.add_field(name="Example", value=".new_semester", inline=False)
        embed.add_field(
            name="Note",
            value=(
                "Removes all course roles from every member "
                "and removes all reaction roles for courses"
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "To initiate a fresh restart for all members and avoid "
                "having old member in courses they are not currently taking."
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["clearCourses"])
    async def clear_courses(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self.get_embed("clear_courses")
        embed.add_field(name="Command", value=".clear_courses <member>", inline=False)
        embed.add_field(name="Aliases", value=".clearCourses", inline=False)
        embed.add_field(
            name="Example", value=".clear_courses @member#1234", inline=False
        )
        embed.add_field(
            name="Note",
            value=("Removes all course roles from every member"),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Allows for easy deletion of all course roles from a member, "
                "useful when either starting a new semester or in cases of spam"
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["clearReactions"])
    async def clear_reactions(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("clear_reactions")
        embed.add_field(
            name="Command", value="`.clear_reactions <member>`", inline=False
        )
        embed.add_field(
            name="Example", value="`.clearReactions @member#1234`", inline=False
        )
        embed.add_field(
            name="Note",
            value="Will remove all course reaction roles added by a member. "
            "There is a short ratelimit every 5 reactions removed due to removing roles from a user.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Allows for easy removal of all course reaction roles from a member, "
                "useful when either starting a new semester or in cases of spam"
            ),
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(
        aliases=["Course Content", "course content", "course-content", "courseContent"]
    )
    async def course_content(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self.get_embed("Course Content")
        embed.add_field(
            name="Commands",
            value="`.course_embed`, `.edit_embed_image`, `.edit_embed_title`, `.edit_course_content`, `.nav_embed`",
            inline=False,
        )
        embed.add_field(
            name=".course_embed",
            value="Stubs out a course embed used for reaction roles",
            inline=False,
        )
        embed.add_field(
            name=".edit_embed_image",
            value="Edits the image of any embedded message",
            inline=False,
        )
        embed.add_field(
            name=".edit_embed_title",
            value="Edits the title of any embedded message",
            inline=False,
        )
        embed.add_field(
            name=".edit_course_content",
            value="Edits the contents of any message",
            inline=False,
        )
        embed.add_field(
            name=".nav_embed",
            value="Creates an instance of a navigation embed used in #course-registration",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["toggleAD"])
    async def toggle_ad(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | toggleAD", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(name="Command", value="`.toggleAD`", inline=False)
        embed.add_field(name="Example", value="`.toggleAD`", inline=False)
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value="Will toggle the auto-delete functionality of the course registration, switching from deleting Husky Bot's messages to not.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows for user to toggle off auto-delete when creating new messages via HuskyBot in `#course-registration` and then toggle it back on to avoid spam from other users.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["newEmbed"])
    async def new_embed(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | newEmbed", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command", value="`.newEmbed <embed-title>, <image-url>`", inline=False
        )
        embed.add_field(
            name="Example",
            value="`.newEmbed Add/Remove ABCD courses, https://imgur.com/PKev2zr.png`",
            inline=False,
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value="Will create a new embedded message with the given title and image. Will also send a course description stub message which can be modified to describe which reactions correspond to each course.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows user to create embedded messages in `#course-registration` to use as differentiable sections and reaction role messages.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["editEmbedImage"])
    async def edit_embed_image(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | editEmbedImage", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command",
            value="`.editEmbedImage [message] [image-url]`",
            inline=False,
        )
        embed.add_field(
            name="Example",
            value="`.editEmbedImage 123456789876543210 https://imgur.com/7obLnAa.png`",
            inline=False,
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value="Will set the embedded message's image to be the provided url.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows user to update any previously sent embedded message's image without resending a new one. Allows for easy updates to update section images if a user decides a new one is needed.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["editEmbedTitle"])
    async def edit_embed_title(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | editEmbedTitle", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command", value="`.editEmbedTitle <message> <title>`", inline=False
        )
        embed.add_field(
            name="Example",
            value="`.editEmbedTitle 123456789876543210 New Title`",
            inline=False,
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value="Will set the embedded message's title to be the provided title.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows users to update any previously sent embedded message's title without resending a new one. Allows for easy updates to update section title if a user decides a new one is needed.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["editCourseContent"])
    async def edit_course_content(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | editCourseContent", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command",
            value="`.editCourseContent [message] [content]`",
            inline=False,
        )
        embed.add_field(
            name="Example",
            value=r"`.editCourseContent 123456789876543210 blah blah blah `\n` blah blah blah`",
            inline=False,
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value=(
                "Will edit any message sent by Husky Bot with the new content.\n"
                "This will **overwrite** the content, **not** add to it.\n"
                r"Any newlines must be indicated by typing `\n`, `shift-enter` will be ignored as a newline."
                "\n"
                "This will not edit the content of an embedded message."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows users to update any course descriptions in `#course-registration` in the case there is new content they need to add or fix.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["ccs"])
    async def course_creation_shortcuts(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(
            desccsiption="To see a page, just add the page name after the `.help` command.\n"
            "Like this: `.help newCourse`",
            colour=discord.Colour.red(),
        )
        embed.set_author(
            name="Help | Course Registration Commands", icon_url=self.avatar
        )
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Commands",
            value="`.newCourse`, `.newCourseReaction`, `.newCourseComplete`,",
            inline=False,
        )
        embed.add_field(
            name="Page newCourse | New Course",
            value="How to use the `.newCourse` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page newCourseReaction | New Course Reaction",
            value="How to use the `.newCourseReaction` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page newCourseComplete | New Course Complete",
            value="How to use the `.newCourseComplete` Command!",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["newCourse"])
    async def new_course(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | newCourse", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command",
            value="`.newCourse <course-name> <channel-name>`",
            inline=False,
        )
        embed.add_field(
            name="Example",
            value="`.newCourse ABCD-1234 course-abcd` or `.newCourse AB-1234 course ab` or `.newCourse ABCD-12XX course-abcd` or `.newCourse AB-12XX course-ab`",
            inline=False,
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value=(
                "Will create a new role with the given course-name if it is the correct format.\n"
                "Will hoist the role to the appropriate position in the hierarchy with the greater course number placing higher.\n"
                "Will create a new channel under the appropriate category.\n"
                "Will position the channel to the appropriate position in the hierarchy relative to the other courses with the lower course number placing higher than the greater course numbers.\n"
                "If it is a course for a new category it will create the category and then place the channel inside.\n"
                "Will setup permissions not allowing members with the Not Registered role to read the messages while only allowing members with the specified course role to read messages.\n"
                "Cannot create a newCourse if there is an existing role for it."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="A shortcut which does not require the user to manually create a role and channel, worry about positioning, or permissions.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["newCourseReaction"])
    async def new_course_reaction(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | newCourseReaction", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command",
            value="`.newCourseReaction <course-role> <course-description>`",
            inline=False,
        )
        embed.add_field(
            name="Example",
            value="`.newCourseReaction @ABCD-1234 abcd description`",
            inline=False,
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value=(
                "Given course-role must already exist.\n"
                "Will find the reaction role embedded message category associated with the course and create a reaction role for the new course with the next letter in the alphabet.\n"
                "Will edit the course description so that the new course's description is listed, and will be placed in the correct order relative to the other courses with the lower course number being listed higher.\n"
                "Will not execute if 26 letters already exist on the category's reaction role message.\n"
                "Will not execute if the given course already has a reaction role on the given message.\n"
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="A shortcut which does not require the user to manually create a reaction role for the course by giving specific information about channel, message_id, reaction and then manually edit another HuskyBot message for the course-description.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["newCourseComplete"])
    async def new_course_complete(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | newCourseComplete", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command",
            value="`.newCourseComplete <course-role> <channel-description>, <course-description>`",
            inline=False,
        )
        embed.add_field(
            name="Example",
            value="`.newCourseComplete ABCD-1234 abcd channel, abcd description`",
            inline=False,
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value="Must have a comma to separate the channel description and course description. (All other specifics pertaining to `.newCourse` and `.newCourseReaction`)",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="An all-in-one shortcut allowing the user to automate all the task of creating a new course carrying out the specifics of `.newCourse` followed by `.newCourseReaction`.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["1"])
    async def activity(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Activity")
        embed.description = (
            "To see more info about a command just add the name after the `.help` command.\n"
            "Like this: `.help playing`"
        )
        embed.add_field(
            name="Commands", value="`.playing`, `.streaming`", inline=False,
        )
        embed.add_field(
            name=".playing",
            value="Shows all the people playing a given activity",
            inline=False,
        )
        embed.add_field(
            name=".streaming",
            value="Shows all the people streaming currently",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group()
    async def playing(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Playing")
        embed.add_field(
            name="Command", value="`.playing <activity_name>`", inline=False,
        )
        embed.add_field(name="Example", value="`.playing spotify`", inline=False)
        embed.add_field(
            name="Note",
            value=(
                "Any activity containing the keyword will be selected (not an exact match). "
                "So `.playing league` would find both League of Legends and Rocket League, for example."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows for a user to find all the members in a server that is playing a certain activity.",
            inline=False,
        )
        await author.send(embed=embed)

    @help.group()
    async def streaming(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Streaming")
        embed.add_field(
            name="Command", value="`.streaming`", inline=False,
        )
        embed.add_field(name="Example", value="`.streaming`", inline=False)
        embed.add_field(
            name="Purpose",
            value="Allows a user to find all the members in a server currently streaming.",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["2"])
    async def day(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Day Date")
        embed.add_field(name="Command", value="`.day <date>`", inline=False)
        embed.add_field(
            name="Example", value="`.day 9/1/2022` or `.day Sept 1, 2022`", inline=False
        )
        embed.add_field(
            name="Note",
            value="If year is not provided, current year is used by default. Year must be less than 10000",
            inline=False,
        )
        embed.add_field(
            name="Date Formats",
            value="mm/dd/yy | mm/dd/YYYY | Month dd, YY | MonthAcronym dd, YY",
            inline=False,
        )
        embed.add_field(
            name="Purpose", value="Determines the day of any given date", inline=False
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["3", "Hours"])
    async def hours(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Hours")
        embed.add_field(
            name="Command", value="`.hours <location>, [day]`", inline=False
        )
        embed.add_field(
            name="Example",
            value="`.hours stwest, monday` or `.hours steast`",
            inline=False,
        )
        embed.add_field(
            name="Note",
            value=(
                "Day is optional. If no day is provided, the current day is used by default.\n"
                "A location can be mulitple words and can be valid under multiple aliases.\n"
                "A comma __must__ be used to separate the location and day. (Case-insensitive)"
            ),
            inline=False,
        )
        embed.add_field(
            name="Possible Days",
            value=(
                "Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, "
                "Sun, Mon, Tues, Wed, Thurs, Fri, Sat, S, U, M, T, W, R, F, "
                "Tu, Tue, Tues, Th, Thu, Thurs, Tomorrow"
            ),
            inline=False,
        )
        embed.add_field(
            name="Supported Locations (as of Apr 2020)",
            value=(
                "Amelia's Taqueria, Argo Tea, Boston Shawarma, Café 716, "
                "Café Crossing, Cappy's, Chicken Lou's, College Convenience, "
                "CVS, Dominos, Faculty Club, Gyroscope, International Village, "
                "Kigo Kitchen, Kung Fu Tea, Outtakes, Panera Bread, Pho and I, "
                "Popeyes Louisiana Kitchen, Qdoba, Rebecca's, Resmail, SquashBusters, "
                "Star Market, Starbucks, Stetson East, Stetson West, Subway, "
                "Sweet Tomatoes, Symphony Market, Tatte, The Egg Shoppe, "
                "The Market, The West End, Tú Taco, Uburger, "
                "University House Of Pizza, Wendy's, Whole Foods, Wings Over, "
                "Wollaston's Market, Wollaston's Market West Village."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Says the hours of operation of select locations and determines whether it's OPEN or CLOSED."
                "Specifies minutes left until closing/opening if less than 1 hour remaining."
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["4", "Ice Cream", "ice cream"])
    async def icecream(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Ice Cream")
        embed.add_field(name="Command", value="`.icecream [day]`", inline=False)
        embed.add_field(
            name="Example", value="`.icecream` or `.icecream monday`", inline=False
        )
        embed.add_field(
            name="Note",
            value="Day is optional. If no day is provided, the current day will be used by default.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Displays what the current ice cream flavors are available any day from the Northeastern Dining Halls."
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["5", "Miscellaneous", "miscellaneous"])
    async def misc(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Miscellaneous")
        embed.add_field(
            name="Commands",
            value="`.ping`, `.echo`, `.flip`, `.menu`, `.invite`",
            inline=False,
        )
        embed.add_field(
            name=".ping",
            value="Sends a message which contains the Discord WebSocket protocol latency",
            inline=False,
        )
        embed.add_field(
            name=".echo",
            value="Repeats anything the user says after the given command",
            inline=False,
        )
        embed.add_field(
            name=".flip",
            value="Flips a coin and says the result (Heads/Tails)",
            inline=False,
        )
        embed.add_field(
            name=".menu",
            value="Sends a link to the Northeastern dining hall menu.",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["6", "Open"])
    async def open(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Open")
        embed.add_field(name="Command", value="`.open <sort>`", inline=False)
        embed.add_field(name="Example", value="`.open` or `.open sort`", inline=False)
        embed.add_field(
            name="Note",
            value=(
                "The sort argument is optional. If none is provided it will display the locations in alphabetical order. "
                "If given, it will display them in order of time to close."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "To see all the open locations at once in either alphabetical order or order of time to close."
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["7", "Reminder"])
    async def reminder(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Reminder")
        embed.add_field(
            name="Command",
            value="`.reminder <your-reminder> in <number> <unit-of-time>`",
            inline=False,
        )
        embed.add_field(
            name="Example", value="`.reminder get laundry in 32 mins`", inline=False
        )
        embed.add_field(
            name="Note",
            value='"in" is a manditory word that __must__ exist between the reminder and the time.',
            inline=False,
        )
        embed.add_field(
            name="Unit of time possibilites",
            value=(
                "sec, secs, second, seconds, s, "
                "min, mins, minute, minutes, m, "
                "hr, hrs, hour, hours, h, "
                "day, days, d, "
                "week, weeks, w"
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Sends a reminder to the user after the specified amount of time has passed",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["8", "Stats"])
    async def stats(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("Stats")
        embed.description = (
            "To see more info about a command just add the name after the `.help` command.\n"
            "Like this: `.help whois`"
        )
        embed.add_field(
            name="Commands",
            value="`.serverinfo`, `.ordered_list_members`, `.whois`, `.join_no`",
            inline=False,
        )
        embed.add_field(
            name=".serverinfo", value="Displays stats about the server", inline=False,
        )
        embed.add_field(
            name=".ordered_list_members",
            value="Sends a list of the members in order of join date",
            inline=False,
        )
        embed.add_field(
            name=".whois",
            value="Sends information about any user in a server",
            inline=False,
        )
        embed.add_field(
            name=".join_no",
            value="Send the information about a user given a join no",
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group()
    async def serverinfo(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("serverinfo")
        embed.add_field(name="Command", value="`.serverinfo`", inline=False)
        embed.add_field(name="Example", value="`.serverinfo`", inline=False)
        embed.add_field(
            name="Purpose",
            value=(
                "Returns an embedded messages with information about the current state of the server. \n"
                "Includes: Server ID, Date Server Created, Server Icon, Server Owner, Region, "
                "Number of Channel Categories, Number of Text Channels, Number of Voice Channels, "
                "Number of Roles, Number of Members, Number of Humans, Number of Bots, "
                "Number of users currently online/idle/dnd, Number of user currently on mobile for each status, "
                "Number of Not Registered users, "
                "Number of users who made a New Account (<1 day old account) before joining the server, "
                "Number of emojis, Verification Level, Number of Active Invites, 2FA State"
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(
        aliases=["orderedListMembers", "lsMembers", "listMembers", "list_members"]
    )
    async def ordered_list_members(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("ordered_list_members")
        embed.add_field(
            name="Command",
            value="`.ordered_list_members [num-members] [output-type]`",
            inline=False,
        )
        embed.add_field(
            name="Example",
            value="`.ordered_list_members 30 mention` or `.ordered_list_members 50` or `.ordered_list_members`",
            inline=False,
        )
        embed.add_field(
            name="Aliases",
            value="`.orderedListMembers`, `.lsMembers`, `listMembers`, `list_members`",
            inline=False,
        )
        embed.add_field(
            name="Note",
            value=(
                "Will default to at least 10 members if no arguments are given. \n"
                "Will default to showing nicknames if no output type is given. \n"
                "Output Types: nick/nickname (user's nickname or username if no nickname), "
                "name (user's username), mention (user mentioned) \n"
                "Includes bot accounts."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Gets a list of members by order of the date they joined the server."
            ),
            inline=False,
        )
        await ctx.messsage.delete()
        await author.send(embed=embed)

    @help.group(aliases=["whoam"])
    async def whois(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("whois")
        embed.add_field(name="Command", value="`.whois [member_name]`", inline=False)
        embed.add_field(name="Aliases", value="`.whoam`", inline=False)
        embed.add_field(
            name="Example",
            value="`.whois discordUser19` or `.whoam I` or `.whois`",
            inline=False,
        )
        embed.add_field(
            name="Permissions",
            value="Administrator/Moderator and Everyone",
            inline=False,
        )
        embed.add_field(
            name="Note",
            value=(
                "Admins/mods can find info about any member."
                "Non-admin/mod members can only find out information about themselves."
                'Will default to the user who sent the command if no arguments are given or the letter "I" is given.'
                "The member search criteria is case-insensitive and does not need to be exact."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Gets information about a specific user. \n"
                "Includes: Member ID, Member Name Including Discriminator, Mentioned member, "
                "Profile Picture, Current Online Status, Date the member joined, "
                "Member's join position in the server, Date the member created a Discord Account, "
                "The roles the member has in the server and the number of roles, "
                "Permissions that the member has in the server overall, "
                "Member's color via the embedded message color"
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["joinNo"])
    async def join_no(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("join_no")
        embed.add_field(name="Command", value="`.join_no <number>`", inline=False)
        embed.add_field(name="Example", value="`.join_no 50`", inline=False)
        embed.add_field(name="Aliases", value="`.joinNo`", inline=False)
        embed.add_field(
            name="Note",
            value="Will send error messages to guide the user if the given number is not within the range of members in the server. Includes bot accounts.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Gets information about a user at a specific join position from a server. \n"
                "Includes: Member ID, Member Name Including Discriminator, Mentioned member, "
                "Profile Picture, Current Online Status, Date the member joined, "
                "Member's join position in the server, Date the member created a Discord Account, "
                "The roles the member has in the server and the number of roles, "
                "Permissions that the member has in the server overall, "
                "Member's color via the embedded message color"
            ),
            inline=False,
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["9", "Suggest"])
    async def suggest(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = self._get_embed("suggest")
        embed.add_field(name="Command", value="`.suggest <your-suggestion>")
        embed.add_field(name="Example", value="`.suggest add course ABCD-1234")
        embed.add_field(
            name="Purpose",
            value=(
                "Allows any member to easily make a suggestion, ping the Admins, "
                "and pin the message in the suggestions channel for visibility."
            ),
        )
        await ctx.message.delete()
        await author.send(embed=embed)

    @help.group(aliases=["8"])
    async def choose(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | choose", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(name="Command", value="`.choose <role-name>`", inline=False)
        embed.add_field(
            name="Example",
            value="`.choose CS-2500` or `.choose cs 2500` or `.choose spring green`",
            inline=False,
        )
        embed.add_field(
            name="Permissions", value="Administrator & Everyone", inline=False
        )
        embed.add_field(
            name="Note",
            value=(
                "Non-admin users can only use this command in `#course-registration`.\n"
                "Non-admin users can only toggle courses in `#course-registration`.\n"
                "Admins can toggle any role and do it anywhere.\n"
                "Role names are case-insensitive, spaces are allowed, and courses do not require a '-' even though it is in the name."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Toggle #course-registration roles without having to search for their reactions in the large channel.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["rr"])
    async def reaction_role(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(
            description="To see a page, just add the page name after the `.help` command.\n"
            "Like this: `.help newrr`",
            colour=discord.Colour.red(),
        )
        embed.set_author(name="Help | Reaction Role Commands", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Commands",
            value="`.newrr`, `.fetchrr`, `.removerr`, `removeallrr`",
            inline=False,
        )
        embed.add_field(
            name="Page newrr | Adding New Reaction Role",
            value="How to use the `.newrr` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page fetchrr | Fetching Reaction Role Information",
            value="How to use the `.fetchrr` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page removerr | Removing a Reaction Role",
            value="How to use the `.removerr` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page removeallrr | Removing All Reaction Roles for Message",
            value="How to use the `.removeallrr` Command!",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group()
    async def newrr(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | newrr", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command",
            value="`.newrr <channel> <message_id> <reaction/emoji> <role>`",
            inline=False,
        )
        embed.add_field(
            name="Example",
            value="`.newrr #rules 123456789876543210 👍 @Student`",
            inline=False,
        )
        embed.add_field(
            name="Note",
            value=(
                "Given **channel** can be in the form of a mentioned channel or just the name.\n"
                "Given **message id** must be a valid message id and a number.\n"
                "Given **emoji** must be a valid emoji in the correct form (Ex: :thumbs_up:).\n"
                "Given **role** can be in the form of a mentioned role or just the name."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows for the user to select a specific message that users can react to with a chosen emoji to get assigned a role and unreact to remove the role.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group()
    async def fetchrr(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | fetchrr", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(name="Command", value="`.fetchrr <message_id>`", inline=False)
        embed.add_field(
            name="Example", value="`.fetchrr 123456789876543210`", inline=False
        )
        embed.add_field(
            name="Note",
            value="Given message id must be a valid message id and a number.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Fetches all the keys, reaction, and roles corresponding to each reaction role for the given message id.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group()
    async def removerr(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | removerr", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(name="Command", value="`.removerr <key>`", inline=False)
        embed.add_field(name="Example", value="`.removerr F0xUOpxMv`", inline=False)
        embed.add_field(
            name="Note",
            value="Given key must be a valid key. Each reaction role is assigned a unique key and can be found in the embedded message upon creation of the reaction role or by using the `.fetchrr` command.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows for the user to delete any reaction role by giving the unique key.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group()
    async def removeallrr(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | removeallrr", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command", value="`.removeallrr <message_id>`", inline=False
        )
        embed.add_field(
            name="Example", value="`.removeallrr 123456789876543210`", inline=False
        )
        embed.add_field(
            name="Note",
            value="Given message id must be a valid message id and a number.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows for the user to delete all reaction roles from a given message at once.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
