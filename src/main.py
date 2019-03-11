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
if os.path.isfile("src/creds.py"):
    from creds import TOKEN  # local TOKEN
else:
    TOKEN = os.environ["TOKEN"]  # TOKEN from Heroku

EXTENSIONS = ['voice', 'help', 'hours', 'reaction']

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


@client.event
async def on_message(message):
    # AutoDelete Dyno Bot's Messages in #course-registration
    # if user has an administrator permissions
    admin = ('administrator', True) in [perm for perm in message.author.permissions_in(message.channel)]
    if not admin and message.channel.id == DYNO_ACTION_LOG_CHANNEL_ID:
        await asyncio.sleep(5)
        await client.delete_message(message)
    # Sends it be like that gif anytime those words are in a sentence
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
    # sends a randomly chosen picture of Aoun anytime Aoun is mentioned
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


@client.event  # says what message was deleted and by whom
async def on_message_delete(message):
    author = message.author
    isBot = author.bot  # if the author of the message is a bot
    if not isBot:
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
    if before_content != after_content:
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
        except discord.errors.InvalidArgument:
            print('InvalidArgument')
        except discord.errors.HTTPException:
            print("HTTPException")


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


# gives the ice-cream flavors on the menu for today
@client.command()
async def icecream(*args):
    POSSIBLE_DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    EST = datetime.now(timezone('US/Eastern'))
    TODAY = EST.strftime("%A").upper()
    day = args[0].upper()
    # if day is given
    if args:
        day = args[0].upper()
        # if valid day
        if day in POSSIBLE_DAYS:
            day = day
        # if given day is tomorrow
        elif day == 'TOMORROW':
            # finds the current day's index in POSSIBLE_DAYS and add 1 getting the next day
            day = POSSIBLE_DAYS[(POSSIBLE_DAYS.index(TODAY)+1) % len(POSSIBLE_DAYS)]
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
@commands.has_permissions(administrator=True)
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
client.run(TOKEN)  # run bot
