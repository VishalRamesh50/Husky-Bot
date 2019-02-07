import discord
from discord.ext import commands
import asyncio
from itertools import cycle
from datetime import datetime
from pytz import timezone
import random
import NUDining
import decimal
from decimal import Decimal
import os
if os.path.isfile("creds.py"):
    from creds import TOKEN  # local TOKEN
else:
    TOKEN = os.environ["TOKEN"]  # TOKEN from Heroku

EXTENSIONS = ['voice']

client = commands.Bot(command_prefix='.')  # bot prefix
client.remove_command('help')  # remove default help command
STATUS = ['With Huskies!', '.help']  # bot statuses

# SERVER SPECIFIC ID'S
DYNO_BOT_ID = '155149108183695360'
COURSE_REGISTRATION_CHANNEL_ID = '485279507582943262'
ADMIN_ID = '485227611375534143'
DYNO_ACTION_LOG_CHANNEL_ID = '485469821417422850'
NOT_REGISTERED_ID = '501184186498154511'
RULES_CHANNEL_ID = '485279439593144362'
COURSE_REGISTRATION_CHANNEL_ID = '485279507582943262'
NOT_REGISTERED_CHANNEL_ID = '501193530325205003'
TEST_CHANNEL_ID = '485217538893021185'
HUSKY_BOT_ID = '485524303518105601'
SUGGESTIONS_CHANNEL_ID = '485467694624407552'
BOT_SPAM_CHANNEL_ID = '531665740521144341'
V_MONEY_ID = '424225320372011008'
SUPERSECSEE_ID = '267792923209236500'
SHWIN_ID = '354084198841188356'
GENERAL_CHANNEL_ID = '497185813264859137'


@client.event  # Bot is Ready to Go
async def on_ready():
    print(f"{client.user.name} is ONLINE!")


async def change_status():
    await client.wait_until_ready()
    msgs = cycle(STATUS)

    while not client.is_closed:
        current_status = next(msgs)
        await client.change_presence(game=discord.Game(name=current_status))  # display status
        await asyncio.sleep(5)  # change status every 5 seconds


# error handler
@client.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.CheckFailure):  # if command was not used with required role
        await client.send_message(channel, 'Insufficient Role')


# Welcome Message
@client.event
async def on_member_join(member):
    welcome_msg = discord.Embed(
        description=f"Hey {member.mention}, welcome to **{member.server}** 🎉! Check your DMs from <@!{HUSKY_BOT_ID}> for further instructions!",
        colour=discord.Colour.red())
    welcome_msg.set_thumbnail(url=f"{member.avatar_url}")
    join_msg = (f"Welcome to the **{member.server}** server {member.mention}!\n\n"
                f":one: Accept the rules by reacting with a 👍 in {client.get_channel(RULES_CHANNEL_ID).mention} to become a Student.\n"
                f":two: Select your year by reacting with a number.\n"
                f":three: Assign yourself a school/major and courses in **#course-registration**.\n"
                f"If you have questions or need help getting registered feel free to DM the Admins or check out the {client.get_channel(NOT_REGISTERED_CHANNEL_ID).mention} channel.\n"
                f"__Server Owner__: <@!{V_MONEY_ID}> __Co-Admins__: <@!{SUPERSECSEE_ID}> & <@!{SHWIN_ID}>\n\n"
                f"We hope that with student collaboration university will be easy and fun.")
    await client.send_message(client.get_channel(GENERAL_CHANNEL_ID), embed=welcome_msg)
    await client.send_message(member, join_msg)


# AutoDelete Dyno Bot's Messages in #course-registration
@client.event
async def on_message(message):
    if message.author.id == DYNO_BOT_ID and message.channel.id == COURSE_REGISTRATION_CHANNEL_ID:
        await asyncio.sleep(5)
        await client.delete_message(message)
    content = message.content
    channel = message.channel
    count = 0
    IT_BE_LIKE_THAT = "IT BE LIKE THAT".split()
    for word in content.upper().split():
        if word in IT_BE_LIKE_THAT:
            IT_BE_LIKE_THAT.remove(word)
            count += 1
    if count >= 4:
        await client.send_message(channel, "https://tenor.com/view/it-really-do-be-like-that-sometimes-like-that-sometimes-gif-12424014")
    AOUN_PICS = ['https://nustudentlife.files.wordpress.com/2016/07/maxresdefault1.jpg',
                 'https://i.redd.it/l2ectyrr30ry.png',
                 'https://i.redd.it/jamxajoqfkhy.png',
                 'https://imgur.com/DWTkyXU',
                 'https://imgur.com/BdWa9YS',
                 'https://imgur.com/dYEgEaM',
                 'https://imgur.com/RTn4rCt',
                 'https://imgur.com/dK8DFjm']
    for word in content.upper().split():
        if word in ["AOUN"]:
            await client.send_message(channel, AOUN_PICS[random.randint(0, len(AOUN_PICS)-1)])
    await client.process_commands(message)


# Removes Not Registered Role from fully registered members or adds it to unregistered ones
@client.event
async def on_member_update(before, after):
    POSSIBLE_YEARS = ['Freshman', 'Sophomore', 'Middler', 'Junior', 'Senior', 'Graduate', 'Newly Admitted']
    POSSIBLE_SCHOOLS = ['EXPLORE', 'COE', 'CCIS', 'CAMD', 'DMSB', 'BCHS', 'CPS', 'CSSH', 'COS']
    STUDENT = ['Student']
    # get Not Registered Role Object
    NOT_REGISTERED_ROLE = discord.utils.get(after.server.roles, name="Not Registered")
    in_years, in_schools, in_student = False, False, False
    # if roles have changed
    if before.roles != after.roles:
        # iterate through members roles
        for role in after.roles:
            # if member's role is a Year
            if role.name in POSSIBLE_YEARS:
                in_years = True
            # if member's role is a School
            elif role.name in POSSIBLE_SCHOOLS:
                in_schools = True
            # if member's role is Student
            elif role.name in STUDENT:
                in_student = True
        if in_years and in_schools and in_student:
            await client.remove_roles(after, NOT_REGISTERED_ROLE)
        else:
            await client.add_roles(after, NOT_REGISTERED_ROLE)


# help command
@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        description='Here are the commands for Husky Bot! The prefix is `.`',
        colour=discord.Colour.red()
    )
    embed.set_author(name='Help', icon_url='https://i.imgur.com/PKev2zr.png')
    embed.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
    if ADMIN_ID in [role.id for role in author.roles]:
        embed.add_field(name='.clear', value='Deletes a certain amount of messages! Must be more than 1!', inline=False)  # clear documentation
        embed.add_field(name='.logout', value='Bot logs out!', inline=False)  # logout documentation
        embed.add_field(name='.introduction', value='Sends HuskyBot Introduction!', inline=False)  # introduction documentation
    embed.add_field(name='.ping', value='Returns Pong!', inline=False)  # ping documentation
    embed.add_field(name='.echo', value='Repeats anything typed after the command!', inline=False)  # echo documentation
    embed.add_field(name='.flip', value='Flips a coin!', inline=False)  # flip documentation
    embed.add_field(name='.menu', value='Generates link to NU Dining menu!', inline=False)  # menu documentation
    embed.add_field(name='.hours', value='Tells whether a chosen dining hall is open or not!', inline=False)  # hours documentation
    embed.add_field(name='.reminder', value="Reminds you anything in any amount of time! Follow this format: `.remind [Reminder] in [Number] [Unit of Time]`", inline=False)  # timer documentation
    embed.add_field(name='.day', value='Tells you what day any date is!', inline=False)  # day documentation
    embed.add_field(name='.invite', value='Generates server invite link!', inline=False)  # invite documentation
    embed.add_field(name='.join', value='Joins voice channel. You must be in a voice channel to use.', inline=False)  # join documentation
    embed.add_field(name='.play', value='Plays any music by searching on YouTube!', inline=False)  # play documentation
    embed.add_field(name='.pause', value='Pauses music!', inline=False)  # pause documentation
    embed.add_field(name='.resume', value='Resumes music!', inline=False)  # resume documentation
    embed.add_field(name='.skip', value='Skips music!', inline=False)  # skip documentation
    embed.add_field(name='.queue', value='Adds music to queue!', inline=False)  # queue documentation
    embed.add_field(name='.display_queue', value='Displays current queue!', inline=False)  # display_queue documentation
    embed.add_field(name='.leave', value='Leaves voice channel! Must be in one in the first place', inline=False)  # leave documentation

    await client.delete_message(ctx.message)  # deletes user's command
    await client.say('Check your DM!')
    await client.send_message(author, embed=embed)  # sends user a DM


# replies Pong! given .ping
@client.command()
async def ping():
    await client.say('Pong!')


# repeats given statement after .echo
@client.command(pass_context=True)
async def echo(ctx, *args):
    message = ctx.message
    output = ''
    for word in args:
        output += word
        output += ' '
    await client.delete_message(message)  # deletes command
    await client.say(output)


# deletes set amount of messages
@client.command(pass_context=True)
@commands.has_role('Admin')
async def clear(ctx, amount=''):
    channel = ctx.message.channel
    messages = []
    if amount == '0':
        await client.say("Cannot delete 0 messages.")
    try:
        async for message in client.logs_from(channel, limit=int(amount)+1):
            messages.append(message)
        await client.delete_messages(messages)
        await client.say(f"{len(messages)-1} messages deleted.")
        await asyncio.sleep(5)
        await client.delete_message(ctx.message)
    except ValueError:
        await client.say("Error: Must use a number.")


# Husky Bot self-introduction
@client.command(pass_context=True)
@commands.has_role('Admin')
async def introduction(ctx):
    message = ctx.message
    await client.delete_message(message)
    await client.say(f":pushpin: **HELLO!** :hand_splayed:\n"
                     f"I am <@!{HUSKY_BOT_ID}>! I was made specifically for the NU server and am constantly being worked on!\n"
                     f":pushpin: **FUNCTIONALITY** :tools:\n"
                     f"If you want a full list of my commands just type `.help` and I'll send you a DM! But some of my functions "
                     f"include generating a link to Northeastern's menu, checking the hours for many dining locations on campus "
                     f"for any day, setting reminders for students, figuring out the day for any date, generating the server's invite "
                     f"link, auto-deleting Dyno Bot's role-toggle messages in {client.get_channel(COURSE_REGISTRATION_CHANNEL_ID).mention}, moderation, "
                     f"music bot commands, and more!\n"
                     f":pushpin: **CONTRIBUTE** :gear: :bulb:\n"
                     f"The commands will work in any channel but we would prefer if you kept it to {client.get_channel(BOT_SPAM_CHANNEL_ID).mention} where you can test out and use them. "
                     f"You guys know this is a community oriented server so if you want to make <@!{HUSKY_BOT_ID}> better, you can inform <@&{ADMIN_ID}> of "
                     f"bugs and ideas in {client.get_channel(SUGGESTIONS_CHANNEL_ID).mention} and <@!{V_MONEY_ID}> will work on them immediately.\n"
                     f":pushpin: **You can make <@!{HUSKY_BOT_ID}> what you want it to be!**")

'''
@client.event  # says what message was deleted and by whom
async def on_message_delete(message):
    author = message.author
    content = message.content
    channel = message.channel
    embed = discord.Embed(
        description=f'**Message sent by {author.mention} deleted in {channel.mention}**\n {content}',
        colour=discord.Colour.red()
    )

    embed.set_author(name=author, icon_url=author.avatar_url)
    embed.set_footer(text=f'ID: {message.id}')
    await client.send_message(client.get_channel(DYNO_ACTION_LOG_CHANNEL_ID), embed=embed)


@client.event  # displays before & after state of edited message
async def on_message_edit(message1, message2):
    author = message1.author
    before_content = message1.content
    channel = message1.channel
    after_content = message2.content
    try:
        embed = discord.Embed(
            description=f'**Message edited in {channel.mention}**',
            colour=discord.Colour.red()
        )

        embed.set_author(name=author, icon_url=author.avatar_url)
        embed.add_field(name='Before', value=before_content, inline=False)
        embed.add_field(name='After', value=after_content, inline=False)
        embed.set_footer(text=f'User ID: {author.id}')
        await client.send_message(client.get_channel(DYNO_ACTION_LOG_CHANNEL_ID), embed=embed)
    except AttributeError:
        print("'PrivateChannel' object has no attribite 'mention'")
    except discord.errors.HTTPException:
        print("HTTPException")


async def not_registered_reminder():  # sends announcement to register 2 times a week
    await client.wait_until_ready()
    reminder = (f":pushpin: <@&{NOT_REGISTERED_ID}> you either haven't registered to become a Student, chosen your year, or declared a major yet!\n"
                f":one: Accept the {client.get_channel(RULES_CHANNEL_ID).mention} by reacting with a :thumbsup:\n"
                f":two: Select your year by reacting with a number."
                f":three: Assign yourself a school/major and courses in {client.get_channel(COURSE_REGISTRATION_CHANNEL_ID).mention}\n"
                f"You now are an official member!")

    while not client.is_closed:
        await client.send_message(client.get_channel(TEST_CHANNEL_ID), reminder)
        await asyncio.sleep(302400)  # 2 times a week
'''


# Reminds the user of anything in a set duration of time
@client.command(pass_context=True)
async def reminder(ctx, *args):
    author = ctx.message.author
    reminder = ''
    original_time = args[len(args)-2]  # user's specified time frame
    try:
        time = Decimal(original_time)  # converts user's time (String) to a Decimal
    except decimal.InvalidOperation:  # if time is not a number
        await client.say(f"You have to use a number for the 2nd to last term.\n"
                         f"Incorrect: `.reminder Husky Bot is cool in five secs`\n"
                         f"Correct: `.reminder Husky Bot is cool in 5 secs`")
    UNIT_OF_TIME = args[-1].lower()
    SECOND_POSSIBILITIES = ('sec', 'secs', 'second', 'seconds', 's')
    MINUTE_POSSIBILITIES = ('min', 'mins', 'minute', 'minutes', 'm')
    HOUR_POSSIBILITIES = ('hr', 'hrs', 'hour', 'hours', 'h')
    DAY_POSSIBILITIES = ('day', 'days', 'd')
    WEEK_POSSIBILITIES = ('week', 'weeks', 'w')
    valid_unit = True
    # converts time to seconds
    if UNIT_OF_TIME in SECOND_POSSIBILITIES:
        time = time
    elif UNIT_OF_TIME in MINUTE_POSSIBILITIES:
        time *= 60
    elif UNIT_OF_TIME in HOUR_POSSIBILITIES:
        time *= 3600
    elif UNIT_OF_TIME in DAY_POSSIBILITIES:
        time *= 86400
    elif UNIT_OF_TIME in WEEK_POSSIBILITIES:
        time *= 604800
    else:
        valid_unit = False
    time = int(time)
    for index in range(len(args)):
        # once then end of the reminder has been reached break
        if index == len(args)-3 and args[index] == 'in':
            break
        else:
            # adds word to reminder
            reminder += args[index]
            reminder += ' '
    # if "in" is not between the reminder and the time
    if "in" != args[len(args)-3]:
        await client.say(f"You must include the word `in` between your reminder and the time.\n"
                         f"Incorrect: `.reminder Husky Bot is cool 5 secs`\n"
                         f"Correct: `.reminder Husky Bot is cool in 5 secs`")
    else:
        if valid_unit:
            await client.say(f"I will remind you about `{reminder}` in `{original_time} {UNIT_OF_TIME}`")
            await asyncio.sleep(time)  # wait for specified time in seconds before sending reminder
            await client.send_message(author, f"Here is your reminder for `{reminder}`")
        else:  # if not a valid unit of time
            await client.say(f"Your unit of measurement must be a second, minute, hour, day, or week.\n"
                             f"Incorrect: `.reminder Husky Bot is cool in 1 month`\n"
                             f"Correct: `.reminder Husky Bot is cool in 4 weeks`")


# generates invite link to server
@client.command()
async def invite():
    await client.say('discord.gg/CP9MBRH')


# generates link to NU dining menu
@client.command()
async def menu():
    await client.say('https://new.dineoncampus.com/Northeastern/menus')


# tells what day a date is
@client.command()
async def day(*args):
    EST = datetime.now(timezone('US/Eastern'))
    POSSIBLE_MONTHS_FULL = ("JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER")
    POSSIBLE_MONTHS_SHORT = ("JAN", "FEB", "MAR", "APR", "MAY", "JUNE", "JULY", "AUG", "SEPT", "OCT", "NOV", "DEC")
    # if date is in MM/DD/(YYYY) format
    if len(args) == 1 and '/' in args[0]:
        args = args[0].split('/')
        month = args[0]
        try:
            if 0 < int(month) <= 12:  # valid month
                month = int(month)
            else:  # invalid month
                await client.say('Month must be 1-12')
        except ValueError:  # month not a number
            await client.say("Month is must be a number.")
    else:  # date in Month Day (Year) format
        month = args[0]
        # if month is not in full form or acryonymed
        if month.upper() not in POSSIBLE_MONTHS_FULL and month.upper() not in POSSIBLE_MONTHS_SHORT:
            await client.say("Please try a valid month.")
        else:
            # convert given month in words to associated numerical month
            for index in range(0, 12):
                if month.upper() == POSSIBLE_MONTHS_FULL[index] or month.upper() == POSSIBLE_MONTHS_SHORT[index]:
                    month = index + 1
                    break
    # if year is given
    if len(args) > 2:
        try:
            year = int(args[2])
        # if year not a number
        except ValueError:
            await client.say("Year must be a number.")
    else:
        # use current year
        year = int(EST.strftime("%Y"))
    try:
        date = int(args[1])
    # if date not a number
    except ValueError:
        await client.say("Date needs to be a number.")
    try:
        given_date = datetime(year, month, date)
    except ValueError:
        if year > 9999:
            await client.say("Year must be less than 10000.")
        else:
            await client.say("Date not a valid day for the month.")
    day = given_date.strftime("%A")
    await client.say(f"{month}/{date}/{year} is a {day}")


# gives the hours of operation for select locations and determines whether open or not
@client.command()
async def hours(*args):
    POSSIBLE_DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    EST = datetime.now(timezone('US/Eastern'))  # EST timezone
    day = ''
    TODAY = EST.strftime("%A").upper()
    hour = int(EST.strftime("%H"))
    minute = int(EST.strftime("%M"))
    valid_location = False  # whether the given location is valid or not
    month = int(EST.strftime("%m"))
    date = int(EST.strftime("%d"))
    year = int(EST.strftime("%Y"))
    comma = False  # if comma is used in input
    valid_day = False  # if a valid day is present in the input
    commaError = False  # if the comma error should be raised
    content = ''
    #  separates content and optional day from argument by comma
    for word in args:
        if comma:
            day = word.upper()
        elif ',' in word:
            content += word[:-1]
            comma = True
        else:
            content += word + ' '
    content = content.upper()  # makes content uppercase
    parse_location_check = False  # indicates if a recognized location is within the content
    parse_day_check = False  # indicates if a valid day is within the content
    # sets up error checking capability for combinations with an without commas
    if comma:
        if day in POSSIBLE_DAYS + ['TOMORROW']:
            valid_day, parse_day_check = True, True
    else:
        content = content.split()
        for option in POSSIBLE_DAYS + ['TOMORROW']:
            if option in content:
                parse_day_check = True
                break
        content = ' '.join(content)
        if not valid_day:
            day = TODAY
            valid_day = True
    # sets the special & holiday string and checks for holidays
    if month == 1 and 18 <= date <= 21 and year == 2019:
        # if specified day is during MLK Weekend
        if day in ['FRIDAY', 'SATURDAY', 'SUNDAY', 'MONDAY']:
            special = 'MLK'
            holiday = " **(Martin Luther King Weekend)**"
            DINING_LOCATIONS = NUDining.MLK_LOCATIONS
    else:
        special, holiday = '', ''
        DINING_LOCATIONS = NUDining.NORMAL_LOCATIONS
    # check if given content is a valid location
    for possibilities in DINING_LOCATIONS.keys():
        if content in possibilities:
            valid_location, parse_location_check = True, True
            break
        # check if a location alias is in the content
        for options in possibilities:
            if options in content:
                parse_location_check = True
    # check for comma error
    if (parse_location_check or (parse_day_check and not valid_location)) and not comma:
        commaError = True
    original_day = day  # day before changing to location specific key
    POSSIBLE_LOCATIONS = ("IV, Steast, Stwest, Outtakes, Kigo's Kitchen, Popeyes, Rebeccas, "
                          "Starbucks, Subway, UBurger, Qdoba, Amelias, Boston Shawarma, "
                          "Cappy's, Chicken Lou's, College Convenience, CVS, Dominos")
    # if a valid day is within the content
    if valid_day:
        # if given day is tomorrow
        if day == 'TOMORROW':
            # finds the current day's index in POSSIBLE_DAYS and add 1 getting the next day
            for index in range(0, len(POSSIBLE_DAYS)):
                if TODAY == POSSIBLE_DAYS[index]:
                    day = POSSIBLE_DAYS[(index+1) % len(POSSIBLE_DAYS)]
                    break
        yesterday = POSSIBLE_DAYS[(POSSIBLE_DAYS.index(day) - 1) % len(POSSIBLE_DAYS)]  # get yesterday
    else:
        await client.say("Error: Not a valid day.")
    # Martin Luther King Weeekend (2019)
    if special == 'MLK':
        for aliases in DINING_LOCATIONS:
            if content in aliases:
                location = DINING_LOCATIONS[aliases]
    # if normal hours
    else:
        for aliases in DINING_LOCATIONS:
            if content in aliases:
                content = aliases[0]  # sets content to full location name
                location = DINING_LOCATIONS[aliases]  # sets location to corresponding dictionary
                # Set given day to location specific keys if necessary
                if 'WEEKDAYS' in location.keys():
                    if day != 'SATURDAY' or day != 'SUNDAY':
                        day = 'WEEKDAYS'
                    if yesterday != 'SATURDAY' or day != 'SUNDAY':
                        yesterday = 'WEEKDAYS'
                if 'WEEKENDS' in location.keys():
                    if day[0] == 'S':
                        day = 'WEEKENDS'
                    if yesterday[0] == 'S':
                        yesterday = 'WEEKENDS'
                if 'EVERYDAY' in location.keys():
                    day, yesterday = 'EVERYDAY', 'EVERYDAY'
    # if given location is a valid location
    if valid_location:
        # if location is closed for the whole day
        if location[day] == "CLOSED":
            await client.say(f"{content} is CLOSED {day}{holiday}.")
        else:
            # TODAY HOURS VARIABLES
            link = location['LINK']  # location's link to hours of operation
            opening = location[day][0]  # opening hour in 24hr format
            opening_hour = opening % 12  # opening hour in 12hr format
            # since 12%12=0, convert to 12
            if opening_hour == 0:
                opening_hour = 12
            opening_minute = location[day][1]
            opening_period = location[day][2]  # AM/PM
            closing = location[day][3]  # closing hour in 24hr format
            closing_hour = closing % 12  # closing hour in 12hr format
            # since 12%12=0, convert to 12
            if closing_hour == 0:
                closing_hour = 12
            closing_minute = location[day][4]
            closing_period = location[day][5]  # AM/PM
            hours_of_operation = f"{content} is open from {opening_hour}:{opening_minute} {opening_period} - {closing_hour}:{closing_minute} {closing_period} {day}{holiday}."
            open = f"{content} is OPEN now! {hours_of_operation}"
            closed = f"{content} is CLOSED now. {hours_of_operation}"
            # YESTERDAY HOURS VARIABLES
            if location[yesterday] != "CLOSED":
                yesterday_closing = location[yesterday][3]  # yesterday's closing_hour 24hr format
                # if yesterday doesn't close in the next day then set to the same as today's closing
                if yesterday_closing <= 24:
                    yesterday_closing = closing
                yesterday_closing_hour = yesterday_closing % 12
                # since 12%12=0, convert to 12
                if yesterday_closing_hour == 0:
                    yesterday_closing_hour = 12
                yesterday_closing_min = location[yesterday][4]  # yesterday's closing minute
                yesterday_closing_period = location[yesterday][5]  # yesterday_closing period
                yesterday_hours_of_operation = f"{content} is open till {yesterday_closing_hour}:{yesterday_closing_min} {yesterday_closing_period} and {hours_of_operation}"
                yesterday_open = f"{content} is OPEN now! {yesterday_hours_of_operation}"
            else:
                # set all of yesterday's variables to today's to avoid undefined variables
                yesterday_closing = closing_hour
                yesterday_closing_hour = closing_hour
                yesterday_closing_min = closing_minute
                yesterday_closing_hour = closing_hour
                yesterday_closing_period = closing_period
                yesterday_hours_of_operation = hours_of_operation
                yesterday_open = open
            # if a day was specified
            if original_day != TODAY:
                await client.say(hours_of_operation)
            else:
                if opening <= hour <= closing or (0 <= hour <= yesterday_closing_hour and yesterday_closing > 24):
                    # if hour is the same as the opening hour
                    if hour == opening:
                        if minute >= int(opening_minute):
                            await client.say(open)
                        else:
                            difference = int(opening_minute) - minute
                            await client.say(f"{closed} It will be opening in {difference} minutes!")
                    # if hour is the same as the closing hour
                    elif hour == closing:
                        if minute < int(closing_minute):
                            difference = int(closing_minute) - minute
                            await client.say(f"{open} It will be closing in {difference} minutes!")
                        else:
                            await client.say(closed)
                    elif hour == yesterday_closing_hour:
                        if minute < int(yesterday_closing_min):
                            difference = int(yesterday_closing_min) - minute
                            await client.say(f"{yesterday_open} It will be closing in {difference} minutes!")
                        else:
                            await client.say(closed)
                    # if hour is not the same as closing hour but there is still 1hr or less until closing
                    elif (closing - hour) == 1:
                        if int(closing_minute) == 0:
                            difference = 60 - minute
                        else:
                            difference = int(closing_minute) - minute
                        await client.say(f"{open} It will be closing in {difference} minutes!")
                    elif (yesterday_closing_hour - hour) == 1:
                        if int(closing_minute) == 0:
                            difference = 60 - minute
                        else:
                            difference = int(closing_minute) - minute
                        await client.say(f"{yesterday_open} It will be closing in {difference} minutes!")
                    else:
                        await client.say(open)
                # if hour is not the same as opening hour but there is still 1hr or less until opening
                elif (opening - hour) == 1:
                    if int(opening_minute) == 0:
                        difference = 60 - minute
                    else:
                        difference = int(opening_minute) - minute
                    await client.say(f"{closed} It will be opening in {difference} minutes!")
                else:
                    await client.say(closed)
        # generates link to respective location's hours of operation
        await client.say(link)
    # if invalid location was provided
    else:
        # if a comma was not used to separate content and day
        if commaError:
            await client.say("Error: You must separate the location & day with a comma.")
        # if content is not a valid location
        else:
            await client.say(f"Error: Location options are: {POSSIBLE_LOCATIONS}")


# gives the ice-cream flavors on the menu for today
@client.command()
async def icecream(*args):
    POSSIBLE_DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    EST = datetime.now(timezone('US/Eastern'))
    TODAY = EST.strftime("%A").upper()
    # if day is given
    if args:
        # if given day is tomorrow
        if args[0].upper() == 'TOMORROW':
            # finds the current day's index in POSSIBLE_DAYS and add 1 getting the next day
            for index in range(0, len(POSSIBLE_DAYS)):
                if TODAY == POSSIBLE_DAYS[index]:
                    day = POSSIBLE_DAYS[(index+1) % len(POSSIBLE_DAYS)]
                    break
        # if valid day
        elif args[0].upper() in POSSIBLE_DAYS:
            day = args[0].upper()
        # if not a valid day
        else:
            await client.say("Error: Not a valid day.")
    # if no day is given
    else:
        # set day to current day
        day = TODAY
    flavors = NUDining.ICE_CREAM_FLAVORS[day]
    await client.say(f"There is {flavors} on {day}.")


# coin flip
@client.command()
async def flip():
    outcome = random.randint(0, 1)
    if outcome == 0:
        await client.say("Heads!")
    else:
        await client.say("Tails!")


# stops bot
@client.command()
@commands.has_role('Admin')
async def logout():
    await client.say("Alright I'll stop now.")
    print(f"{client.user.name} is logging out.")
    await client.logout()


# loads all extensions
if __name__ == '__main__':
    for extension in EXTENSIONS:
        try:
            client.load_extension(extension)
        except Exception as error:
            print(f"{extension} cannot be loaded. [{error}]")
client.loop.create_task(change_status())  # iniate loop for status
# client.loop.create_task(not_registered_reminder())  # reminder for not-registered channel
client.run(TOKEN)  # run bot
