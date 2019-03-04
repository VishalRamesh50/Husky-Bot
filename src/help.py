import discord
from discord.ext import commands


class Help:
    def __init__(self, client):
        self.client = client

    # help command
    @commands.command(pass_context=True)
    async def help(self, ctx, *args):
        author = ctx.message.author
        channel = ctx.message.channel
        try:
            selection = args[0].upper()
        except IndexError:
            selection = 'HELP'
        # if user has administrator permissions
        admin = ('administrator', True) in [perm for perm in author.permissions_in(channel)]
        if selection == 'HELP':
            embed = discord.Embed(
                description=("To see a page, just add the page number after the `.help` command.\n"
                             "Like this: `.help 1`"),
                colour=discord.Colour.red()
            )
            embed.set_author(name='Help', icon_url=self.client.user.avatar_url)
            embed.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
            if admin:
                embed.add_field(name='Page 0 | Admin', value="Admin Commands", inline=False)  # Admin page
            embed.add_field(name='Page 1 | Reminder', value='How to use Reminder Command!', inline=False)  # reminder page
            embed.add_field(name='Page 2 | Hours', value='How to use Hours Command!', inline=False)  # hours page
            embed.add_field(name='Page 3 | Ice Cream', value='How to use Ice Cream Command!', inline=False)  # ice-cream page
            embed.add_field(name='Page 4 | Day Date', value='How to use Day Date Command!', inline=False)  # day date page
            embed.add_field(name='Page 5 | Music', value='How to use Music Commands!', inline=False)  # music page
            embed.add_field(name='Page 6 | Miscellaneous', value="How to use Miscellaneous Commands!", inline=False)  # miscellaneous page
            await self.client.say(f"Check your DM {author.mention}!")
            await self.client.delete_message(ctx.message)  # deletes user's command
            await self.client.send_message(author, embed=embed)  # sends user a DM
        if admin and selection == '0':
            # admin help page
            admin = discord.Embed(colour=discord.Colour.red())
            admin.set_author(name='Help | Admin-Only Commands', icon_url=self.client.user.avatar_url)
            admin.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
            admin.add_field(name='.clear', value='Deletes a certain amount of messages! Must be more than 0!', inline=False)  # clear documentation
            admin.add_field(name='.logout', value='Bot logs out!', inline=False)  # logout documentation
            admin.add_field(name='.introduction', value='Sends HuskyBot Introduction!', inline=False)  # introduction documentation
            await self.client.delete_message(ctx.message)  # deletes user's command
            await self.client.say(f"Check your DM {author.mention}!")
            await self.client.send_message(author, embed=admin)  # sends user a DM
        if selection == '1':
            # admin help page
            reminder = discord.Embed(colour=discord.Colour.red())
            reminder.set_author(name='Help | Reminder', icon_url=self.client.user.avatar_url)
            reminder.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
            reminder.add_field(name='Command', value='`.reminder [insert-reminder-here] in [number] [unit-of-time]`', inline=False)
            reminder.add_field(name='Example', value='`.reminder get laundry in 32 mins`', inline=False)
            reminder.add_field(name='Note', value='"in" is a manditory word that __must__ exist between the reminder and the time. (Case-insensitive)', inline=False)
            reminder.add_field(name='Unit of time possibilites', value='second, seconds, secs, sec, s, minutes, mins, min, m, hour, hours, hr, hrs, h, day, days, d, week, weeks, w', inline=False)
            reminder.add_field(name='Purpose', value='Confirmation message will be sent and user will receive a DM in the specified duration of time.', inline=False)
            await self.client.delete_message(ctx.message)  # deletes user's command
            await self.client.say(f"Check your DM {author.mention}!")
            await self.client.send_message(author, embed=reminder)  # sends user a DM
        if selection == '2':
            # admin help page
            hours = discord.Embed(colour=discord.Colour.red())
            hours.set_author(name='Help | Hours', icon_url=self.client.user.avatar_url)
            hours.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
            hours.add_field(name='Command', value='`.hours [location], [day]`', inline=False)
            hours.add_field(name='Example', value='`.hours stwest, monday`', inline=False)
            hours.add_field(name='Note', value=('Day is optional. If no day is provided, the current day is used by default.\n'
                                                'A location can be mulitple words and can be valid under multiple aliases.\n'
                                                'A comma __must__ be used to separate the location and day. (Case-insensitive)'), inline=False)
            hours.add_field(name='Possible Days', value='Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sun, Mon, Tues, Wed, Thurs, Fri, Sat, Tomorrow', inline=False)
            hours.add_field(name='Supported Locations (as of Feb 2019)', value=("International Village, Stetson East, Stetson West, Outtakes, Argo Tea, "
                                                                                "Café 716, Café Crossing, Faculty Club, Kigo's Kitchen, The Market, Popeyes, "
                                                                                "Rebecca's, Starbucks, Subway, Sweet Tomatoes, The West End, UBurger, Za'tar, "
                                                                                "Qdoba, Amelia's Taqueria, Boston Shawarma, Cappy's, Chicken Lou's, "
                                                                                " College Convenience, CVS, Dominos, Resmail, Gyroscope, Panera Bread, Pho and I, "
                                                                                "Star Market, Symphony Market, University House of Pizza, Whole Foods, Wings Over."), inline=False)
            hours.add_field(name='Purpose', value=("Says the hours of operation of select locations and determines whether it's OPEN or CLOSED."
                                                   "Specifies minutes left until closing/opening if less than 1 hour remaining."), inline=False)
            await self.client.delete_message(ctx.message)  # deletes user's command
            await self.client.say(f"Check your DM {author.mention}!")
            await self.client.send_message(author, embed=hours)  # sends user a DM
        if selection == '3':
            # admin help page
            ice_cream = discord.Embed(colour=discord.Colour.red())
            ice_cream.set_author(name='Help | Ice Cream', icon_url=self.client.user.avatar_url)
            ice_cream.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
            ice_cream.add_field(name='Command', value='`.icecream [day]`', inline=False)
            ice_cream.add_field(name='Example', value='`.icecream monday`', inline=False)
            ice_cream.add_field(name='Note', value='Day is optional. If no day is provided, the current day will be used by default.', inline=False)
            ice_cream.add_field(name='Purpose', value=('Displays what the current ice cream flavors are available any day from the Northeastern Dining Halls.'), inline=False)
            await self.client.delete_message(ctx.message)  # deletes user's command
            await self.client.say(f"Check your DM {author.mention}!")
            await self.client.send_message(author, embed=ice_cream)  # sends user a DM
        if selection == '4':
            # admin help page
            day_date = discord.Embed(colour=discord.Colour.red())
            day_date.set_author(name='Help | Day Date', icon_url=self.client.user.avatar_url)
            day_date.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
            day_date.add_field(name='Command', value='`.day [date]`', inline=False)
            day_date.add_field(name='Example', value='`.day 9/1/2022` or `.day Sept 1 2022`', inline=False)
            day_date.add_field(name='Note', value='If year is not provided, current year is used by default. However, year is manditory for MM/DD/YYYY format. Year must be less than 10000', inline=False)
            day_date.add_field(name='Date Formats', value='MM/DD/YYYY, Month Day Year, Month Day', inline=False)
            day_date.add_field(name='Purpose', value='Determines the day of any given date', inline=False)
            await self.client.delete_message(ctx.message)  # deletes user's command
            await self.client.say(f"Check your DM {author.mention}!")
            await self.client.send_message(author, embed=day_date)  # sends user a DM
        if selection == '5':
            # admin help page
            music = discord.Embed(colour=discord.Colour.red())
            music.set_author(name='Help | Music', icon_url=self.client.user.avatar_url)
            music.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
            music.add_field(name='Commands', value='`.join`, `.play`, `.pause`, `.resume`, `.skip`, `.queue`, `.display_queue`, `.leave`', inline=False)
            music.add_field(name='.join', value='Joins the voice channel the user is currently in', inline=False)
            music.add_field(name='.play', value='Plays music when given either a name or a url', inline=False)
            music.add_field(name='.pause', value=' Pauses current music', inline=False)
            music.add_field(name='.resume', value='Resumes current music', inline=False)
            music.add_field(name='.skip', value='Skips current music. Stops music if only 1 song left.', inline=False)
            music.add_field(name='.queue', value='Adds a song to the queue', inline=False)
            music.add_field(name='.display_queue', value="Displays the bot's current music queue", inline=False)
            music.add_field(name='.leave', value='Bot leaves the voice channel', inline=False)
            await self.client.delete_message(ctx.message)  # deletes user's command
            await self.client.say(f"Check your DM {author.mention}!")
            await self.client.send_message(author, embed=music)  # sends user a DM
        if selection == '6':
            # admin help page
            misc = discord.Embed(colour=discord.Colour.red())
            misc.set_author(name='Help | Miscellaneous', icon_url=self.client.user.avatar_url)
            misc.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
            misc.add_field(name='Commands', value='`.ping`, `.echo`, `.flip`, `.menu`, `.invite`', inline=False)
            misc.add_field(name='.ping', value='Returns pong!', inline=False)
            misc.add_field(name='.echo', value='Repeats anything the user says after the given command', inline=False)
            misc.add_field(name='.flip', value='Flips a coin and says the result (Heads/Tails)', inline=False)
            misc.add_field(name='.menu', value="Generates a link to Northeastern's menu.", inline=False)
            misc.add_field(name='.invite', value='Generates an invite link to the NU Discord Server.', inline=False)
            await self.client.delete_message(ctx.message)  # deletes user's command
            await self.client.say(f"Check your DM {author.mention}!")
            await self.client.send_message(author, embed=misc)  # sends user a DM


def setup(client):
    client.add_cog(Help(client))
