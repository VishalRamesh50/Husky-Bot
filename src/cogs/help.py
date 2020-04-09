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
        if admin:
            embed.add_field(name="Aoun", value="How to use Aoun commands!")
            embed.add_field(
                name="April Fools", value="How to use April Fools commands!"
            )
            if mod:
                embed.add_field(name="Clear", value="How to use the clear command!")
            embed.add_field(name="Loader", value="How to use Loader commands!")
            embed.add_field(name="Reaction", value="How to use Reaction commands!")
            embed.add_field(name="Twitch", value="How to use Twitch commands!")

        embed.add_field(name="Page 1 | Activity", value="How to use activity commands!")
        embed.add_field(name="Page 2 | Day", value="How to use the day command!")
        embed.add_field(
            name="Page 3 | Ice Cream", value="How to use the icecream command!"
        )
        embed.add_field(
            name="Page 4 | Miscellaneous", value="How to use Miscellaneous commands!"
        )
        embed.add_field(
            name="Page 5 | Reminder", value="How to use the reminder command!"
        )
        embed.add_field(name="Page 6 | Stats", value="How to use Stats commands!")
        embed.add_field(
            name="Page 7 | Suggestion", value="How to use the suggestion command!"
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["0"])
    async def clear(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author

        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | clear", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command", value="`.clear <number> [member]`", inline=False
        )
        embed.add_field(
            name="Example",
            value="`.clear 20` or `.clear 10 @member#1234`",
            inline=False,
        )
        embed.add_field(name="Permissions", value="Manage Messages", inline=False)
        embed.add_field(name="Note", value=("Must be greater than 0."), inline=False)
        embed.add_field(
            name="Purpose",
            value="Clears the last given number of messages in the channel or the ones specifically from a given member.",
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

    @help.group(aliases=["3"])
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

    @help.group(aliases=["4", "miscellaneous"])
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

    @help.group(aliases=["5"])
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

    @help.group()
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
            name="Page whois | Member Info",
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

    @help.group()
    async def ordered_list_members(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | orderedListMembers", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command",
            value="`.orderedListMembers [number of members] [outputType]`",
            inline=False,
        )
        embed.add_field(
            name="Example",
            value="`.orderedListMembers 30 mention` or `.orderedListMembers 50` or `.orderedListMembers`",
            inline=False,
        )
        embed.add_field(
            name="Permissions", value="Administrator or Moderator", inline=False
        )
        embed.add_field(
            name="Note",
            value=(
                "Will default to 10 members if no arguments are given. \n"
                "If there are less than 10 members, it will get all the members. \n"
                "Will default to showing nicknames if no output type is given. \n"
                "OutputTypes: nick/nickname (user's nickname or username if no nickname), name (user's username), mention (user mentioned) \n"
                "Includes bot accounts."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Returns a list of members, in an embedded message by order of the date they joined the server."
            ),
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["joinNo"])
    async def join_no(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | joinNo", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(name="Command", value="`.joinNo [number]`", inline=False)
        embed.add_field(name="Example", value="`.joinNo 50`", inline=False)
        embed.add_field(
            name="Permissions", value="Administrator or Moderator", inline=False
        )
        embed.add_field(
            name="Note",
            value="Will send error messages to guide the user if the given number is not within the range of members in the server. Includes bot accounts.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Returns an embedded messages with information about the current state of the server. \n"
                "Includes: Member ID, Member Name Including Discriminator, Mentioned member, "
                "Profile Picture, Current Online Status, Date the member joined, "
                "Member's join position in the server, Date the member created a Discord Account, "
                "The roles the member has in the server and the number of roles, "
                "Permissions that the member has in the server overall, "
                "Member's color via the embedded message color"
            ),
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["2"])
    async def hours(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | Hours", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command", value="`.hours <location>, [day]`", inline=False
        )
        embed.add_field(name="Example", value="`.hours stwest, monday`", inline=False)
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
                "Sun, Mon, Tues, Wed, Thurs, Fri, Sat, Tomorrow, S, U, M, T, W, R, F, "
                "Tu, Tue, Tues, Th, Thu, Thurs"
            ),
            inline=False,
        )
        embed.add_field(
            name="Supported Locations (as of Jan 2020)",
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
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["3"])
    async def open(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | Open", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(name="Command", value="`.open <sort>`", inline=False)
        embed.add_field(name="Example", value="`.open` or `.open sort`", inline=False)
        embed.add_field(
            name="Note",
            value=(
                "The argument is optional. If none is provided it will display the locations in alphabetical order. "
                "If given, it will display them in order of time to close."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "To see all the available locations at once in either alphabetical order or order of time to close."
            ),
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
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

    @help.group(aliases=["9"])
    async def whois(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | whois", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
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
                "Admins can find info about any member."
                "Non-admin/mod members can use this command to find out information about themselves."
                'Will default to the user who sent the command if no arguments are given or the letter "I" is given.'
                "Will search for members with spaces, is case-insensitive, and will check if the argument is within another member name."
            ),
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value=(
                "Returns an embedded messages with information about the current state of the server. \n"
                "Includes: Member ID, Member Name Including Discriminator, Mentioned member, "
                "Profile Picture, Current Online Status, Date the member joined, "
                "Member's join position in the server, Date the member created a Discord Account, "
                "The roles the member has in the server and the number of roles, "
                "Permissions that the member has in the server overall, "
                "Member's color via the embedded message color"
            ),
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

    @help.group(aliases=["cr"])
    async def course_registration(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(
            description="To see a page, just add the page name after the `.help` command.\n"
            "Like this: `.help toggleAD`",
            colour=discord.Colour.red(),
        )
        embed.set_author(
            name="Help | Course Registration Commands", icon_url=self.avatar
        )
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Commands",
            value="`.toggleAD`, `.choose`, `.newSemester`, `.clearCourses`, `clearReactions`, `newEmbed`, `editEmbedImage`, `editEmbedTitle`, `editCourseContent`",
            inline=False,
        )
        embed.add_field(
            name="Page toggleAD | Toggling AutoDelete",
            value="How to use the `.toggleAD` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page choose | Toggle Courses",
            value="How to use the `.choose` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page newSemester | New Semester",
            value="How to use the `.newSemester` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page clearCourses | Clear Courses",
            value="How to use the `.clearCourses` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page clearReactions | Clear Reactions",
            value="How to use the `.clearReactions` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page newEmbed | New Course Reaction Embed Message",
            value="How to use the `.newEmbed` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page editEmbedImage | Edit Embedded Message Image",
            value="How to use the `.editEmbedImage` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page editEmbedTitle | Edit Embedded Message Title",
            value="How to use the `.editEmbedTitle` Command!",
            inline=False,
        )
        embed.add_field(
            name="Page editCourseContent | Edit Course Content",
            value="How to use the `.editCourseContent` Command!",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
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

    @help.group(aliases=["newSemester"])
    async def new_semester(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | newSemester", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(name="Command", value="`.newSemester`", inline=False)
        embed.add_field(name="Example", value="`.newSemester`", inline=False)
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value="Will remove all courses from every member in the server.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="To initiate a fresh restart for all members and avoid having old members in courses they are not currently taking.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["clearCourses"])
    async def clear_courses(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | clearCourses", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(name="Command", value="`.clearCourses <member>`", inline=False)
        embed.add_field(
            name="Example", value="`.clearCourses @User123#1234`", inline=False
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note", value="Will remove all courses from a member.", inline=False
        )
        embed.add_field(
            name="Purpose",
            value="Allows for easy deletion of all course roles from a user for specific cases especially spam.",
            inline=False,
        )
        await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
        await author.send(embed=embed)

    @help.group(aliases=["clearReactions"])
    async def clear_reactions(self, ctx: commands.Context) -> None:
        author: Union[discord.Member, discord.User] = ctx.author
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Help | clearReactions", icon_url=self.avatar)
        embed.set_thumbnail(url=self.question_mark)
        embed.add_field(
            name="Command", value="`.clearReactions <member>`", inline=False
        )
        embed.add_field(
            name="Example", value="`.clearReactions @User123#1234`", inline=False
        )
        embed.add_field(name="Permissions", value="Administrator", inline=False)
        embed.add_field(
            name="Note",
            value="Will remove all reactions given by a member in the `#course-registration` channel. There is a short timeout every 5 reactions removed if they are tied to a reaction role which the user currently has.",
            inline=False,
        )
        embed.add_field(
            name="Purpose",
            value="Allows for easy removal of all reactions from a user in `#course-registration` for specific cases especially spam.",
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


def setup(client):
    client.add_cog(Help(client))
