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
try:
    from creds import TOKEN  # local TOKEN
except Exception:
    TOKEN = os.environ["TOKEN"]  # TOKEN from Heroku

# EXTENSIONS = ['help', 'hours', 'reaction', 'misc', 'aprilFools', 'activity', 'suggestion', 'voice']
EXTENSIONS = ['help', 'hours', 'reaction', 'misc', 'aprilFools', 'activity', 'stats', 'newSemester']

client = commands.Bot(command_prefix='.')  # bot prefix
client.remove_command('help')  # remove default help command
STATUS = ['With Huskies!', '.help']  # bot statuses

# SERVER SPECIFIC ID'S
ACTION_LOG_CHANNEL_ID = 485469821417422850
RULES_CHANNEL_ID = 485279439593144362
COURSE_REGISTRATION_CHANNEL_ID = 485279507582943262
NOT_REGISTERED_CHANNEL_ID = 501193530325205003
SUGGESTIONS_CHANNEL_ID = 485467694624407552
BOT_SPAM_CHANNEL_ID = 531665740521144341
WELCOME_CHANNEL_ID = 557325274534903815
V_MONEY_ID = 424225320372011008
SUPERSECSEE_ID = 267792923209236500
SHWIN_ID = 354084198841188356


@client.event  # Bot is Ready
async def on_ready():
    print(f"{client.user.name} is ONLINE!")


async def change_status():
    await client.wait_until_ready()
    msgs = cycle(STATUS)

    while not client.is_closed():
        current_status = next(msgs)
        await client.change_presence(activity=discord.Game(current_status))  # display status
        await asyncio.sleep(5)  # change status every 5 seconds


# error handler
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        print(error)
        if (str(error) == "The check functions for command ping failed."
                or str(error) == "The check functions for command whois failed."):
            await ctx.message.delete()
            channel = client.get_channel(BOT_SPAM_CHANNEL_ID)
            await ctx.send("Not here! Try again in" + channel.mention, delete_after=5)


# disable DM commands
@client.check
async def guild_only(ctx):
    return ctx.guild is not None


# Welcome Message
@client.event
async def on_member_join(member):
    guild = member.guild
    NOT_REGISTERED_ROLE = discord.utils.get(guild.roles, name="Not Registered")
    NOT_REGISTERED_CHANNEL = client.get_channel(NOT_REGISTERED_CHANNEL_ID)
    RULES_CHANNEL = client.get_channel(RULES_CHANNEL_ID)
    WELCOME_CHANNEL = client.get_channel(WELCOME_CHANNEL_ID)
    HUSKY_BOT = guild.get_member(client.user.id)
    V_MONEY = guild.get_member(V_MONEY_ID)
    SUPERSECSEE = guild.get_member(SUPERSECSEE_ID)
    SHWIN = guild.get_member(SHWIN_ID)

    # give new member Not Registered Role on join
    await member.add_roles(NOT_REGISTERED_ROLE)

    welcome_msg = discord.Embed(
        description=f"Hey {member.mention}, welcome to **{guild}** 🎉! Check your DMs from {HUSKY_BOT.mention} for further instructions!",
        colour=discord.Colour.red())
    welcome_msg.set_thumbnail(url=f"{member.avatar_url}")
    join_msg = (f"Welcome to the **{guild}** server {member.mention}!\n\n"
                f":one: Accept the rules by reacting with a 👍 in {RULES_CHANNEL.mention} to become a Student.\n"
                f":two: Select your year by reacting with a number.\n"
                f":three: Assign yourself a school/major and courses in **#course-registration**.\n"
                f"If you have questions or need help getting registered feel free to DM the Admins or check out the {NOT_REGISTERED_CHANNEL.mention} channel.\n"
                f"__Server Owner__: {V_MONEY.mention} __Co-Admins__: {SUPERSECSEE.mention} & {SHWIN.mention}\n"
                f"**We hope that with student collaboration university will be easy and fun.**\n\n"
                f"If you need help using this bot just type `.help` in any channel!")
    await WELCOME_CHANNEL.send(embed=welcome_msg)
    await member.send(join_msg)


@client.event
async def on_message(message):
    author = message.author
    channel = message.channel
    # if author exists (message not a webhook) & user has an administrator permissions
    admin = author.permissions_in(channel).administrator if author else False
    # AutoDelete User Messages in #course-registration
    if (not admin or author.bot) and message.channel.id == COURSE_REGISTRATION_CHANNEL_ID:
        await asyncio.sleep(5)
        await message.delete()

    # Sends "it be like that" gif anytime those words are in a sentence
    content = message.content
    count = 0
    IT_BE_LIKE_THAT = "IT BE LIKE THAT".split()
    for word in content.upper().split():
        if word in IT_BE_LIKE_THAT:
            IT_BE_LIKE_THAT.remove(word)
            count += 1
    if count >= 4:
        await channel.send("https://tenor.com/view/it-really-do-be-like-that-sometimes-like-that-sometimes-gif-12424014")

    AOUN_PICS = ['https://nustudentlife.files.wordpress.com/2016/07/maxresdefault1.jpg',
                 'https://i.redd.it/l2ectyrr30ry.png',
                 'https://i.redd.it/jamxajoqfkhy.png',
                 'https://imgur.com/DWTkyXU',
                 'https://imgur.com/BdWa9YS',
                 'https://imgur.com/dYEgEaM',
                 'https://imgur.com/RTn4rCt',
                 'https://imgur.com/dK8DFjm',
                 'https://i.imgur.com/CZxENli.jpg',
                 'https://i.imgur.com/fDyw1Jl.jpg',
                 'https://i.imgur.com/eqTxbiQ.jpg',
                 'https://i.imgur.com/GbyVuHu.jpg',
                 'https://i.imgur.com/jUtM6jo.jpg']
    # sends a randomly chosen picture of Aoun anytime Aoun is mentioned
    for word in content.upper().split():
        if word == "AOUN":
            await channel.send(AOUN_PICS[random.randint(0, len(AOUN_PICS)-1)])
    await client.process_commands(message)


# Removes Not Registered Role from fully registered members or adds it to unregistered ones
@client.event
async def on_member_update(before, after):
    POSSIBLE_YEARS = ['Freshman', 'Sophomore', 'Middler', 'Junior', 'Senior', 'Graduate']
    POSSIBLE_SCHOOLS = ['EXPLORE', 'COE', 'CCIS', 'CAMD', 'DMSB', 'BCHS', 'CPS', 'CSSH', 'COS']
    STUDENT = ['Student']
    SPECIAL_ROLES = ['Newly Admitted', 'Guest']
    # get Not Registered Role Object
    NOT_REGISTERED_ROLE = discord.utils.get(after.guild.roles, name="Not Registered")
    in_years, in_schools, in_student, is_special = False, False, False, False
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
            elif role.name in SPECIAL_ROLES:
                is_special = True
        try:
            if after.bot or (in_student and ((in_years and in_schools) or is_special)):
                await after.remove_roles(NOT_REGISTERED_ROLE)
            else:
                await after.add_roles(NOT_REGISTERED_ROLE)
        except discord.Forbidden:
            pass


# deletes set amount of messages
@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=1):
    amount = int(amount)
    channel = ctx.channel
    if amount <= 0:
        await ctx.send("Cannot delete less than 1 message.")
    else:
        deleted_messages = await channel.purge(limit=amount+1)
        await ctx.send(f"{len(deleted_messages)-1} messages deleted.", delete_after=5)


# Husky Bot self-introduction
@client.command()
@commands.has_permissions(administrator=True)
async def introduction(ctx):
    message = ctx.message
    guild = ctx.guild
    COURSE_REGISTRATION_CHANNEL = client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
    BOT_SPAM_CHANNEL = client.get_channel(BOT_SPAM_CHANNEL_ID)
    SUGGESTIONS_CHANNEL = client.get_channel(SUGGESTIONS_CHANNEL_ID)
    HUSKY_BOT = guild.get_member(client.user.id)
    V_MONEY = guild.get_member(V_MONEY_ID)
    ADMIN_ROLE = discord.utils.get(guild.roles, name="Admin")
    await message.delete()
    await ctx.send(f":pushpin: **HELLO!** :hand_splayed:\n"
                   f"I am {HUSKY_BOT.mention}! I was made specifically for the {guild.name} server and am constantly being worked on!\n"
                   f":pushpin: **FUNCTIONALITY** :tools:\n"
                   f"If you want a full list of my commands just type `.help` and I'll send you a DM! But some of my functions "
                   f"include generating a link to Northeastern's menu, checking the hours for many dining locations on campus "
                   f"for any day, setting reminders for students, figuring out the day for any date, generating the server's invite "
                   f"link, auto-deleting role-toggle messages in {COURSE_REGISTRATION_CHANNEL.mention}, moderation, "
                   f"music bot commands, and more!\n"
                   f":pushpin: **CONTRIBUTE** :gear: :bulb:\n"
                   f"The commands will work in any channel but we would prefer if you kept it to {BOT_SPAM_CHANNEL.mention} where you can test out and use them. "
                   f"You guys know this is a community oriented server so if you want to make {HUSKY_BOT.mention} better, you can inform {ADMIN_ROLE.mention} of "
                   f"bugs and ideas in {SUGGESTIONS_CHANNEL.mention} and {V_MONEY.mention} will work on them immediately.\n"
                   f":pushpin: **You can make {HUSKY_BOT.mention} what you want it to be!**")


@client.event  # says what message was deleted and by whom
async def on_message_delete(message):
    ACTION_LOG_CHANNEL = client.get_channel(ACTION_LOG_CHANNEL_ID)
    author = message.author
    isBot = author.bot  # if the author of the message is a bot
    EST = datetime.now(timezone('US/Eastern'))  # EST timezone
    if not isBot:
        try:
            content = message.content
            channel = message.channel
            attachments = message.attachments
            embed = discord.Embed(
                description=f'**Message sent by {author.mention} deleted in {channel.mention}**\n {content}',
                timestamp=EST,
                colour=discord.Colour.red()
            )
            embed.set_author(name=author, icon_url=author.avatar_url)
            embed.set_footer(text=f'ID: {message.id}')
            await ACTION_LOG_CHANNEL.send(embed=embed)

            for a in attachments:
                embed = discord.Embed(
                    title='Deleted Attachment',
                    description=f'**Attachment sent by {author.mention} deleted in {channel.mention}**\n',
                    timestamp=EST,
                    colour=discord.Colour.red()
                )
                embed.set_image(url=a.proxy_url)
                embed.add_field(name='Cached URL', value=f"[Link]({a.proxy_url})")
                await ACTION_LOG_CHANNEL.send(embed=embed)
        except discord.errors.HTTPException as e:
            print(e)


@client.event  # displays before & after state of edited message
async def on_message_edit(before, after):
    ACTION_LOG_CHANNEL = client.get_channel(ACTION_LOG_CHANNEL_ID)
    author = before.author
    channel = before.channel
    before_content = before.content
    after_content = after.content
    if before_content != after_content:
        try:
            embed = discord.Embed(
                description=f'**[Message edited in]({after.jump_url}){channel.mention}**',
                colour=discord.Colour.gold()
            )
            embed.set_author(name=author, icon_url=author.avatar_url)
            embed.add_field(name='Before', value=before_content, inline=False)
            embed.add_field(name='After', value=after_content, inline=False)
            embed.set_footer(text=f'User ID: {author.id}')
            await ACTION_LOG_CHANNEL.send(embed=embed)
        except discord.errors.HTTPException as e:
            print(e)


# Reminds the user of anything in a set duration of time
@client.command()
async def reminder(ctx, *args):
    await ctx.message.delete()  # delete command
    author = ctx.author
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
        await ctx.send(f"You must include the word `in` between your reminder and the time.\n"
                       f"Incorrect: `.reminder Husky Bot is cool 5 secs`\n"
                       f"Correct: `.reminder Husky Bot is cool in 5 secs`")
    else:
        if valid_unit:
            await author.send(f"I will remind you about `{reminder}` in `{original_time} {UNIT_OF_TIME}`")
            await asyncio.sleep(time)  # wait for specified time in seconds before sending reminder
            await author.send(f"Here is your reminder for `{reminder}`")
        else:  # if not a valid unit of time
            await ctx.send(f"Your unit of measurement must be a second, minute, hour, day, or week.\n"
                           f"Incorrect: `.reminder Husky Bot is cool in 1 month`\n"
                           f"Correct: `.reminder Husky Bot is cool in 4 weeks`")


# tells what day a date is
@client.command()
async def day(ctx, *args):
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
                await ctx.send('Month must be 1-12')
        except ValueError:  # month not a number
            await ctx.send("Month is must be a number.")
    else:  # date in Month Day (Year) format
        month = args[0]
        # if month is not in full form or acryonymed
        if month.upper() not in POSSIBLE_MONTHS_FULL and month.upper() not in POSSIBLE_MONTHS_SHORT:
            await ctx.send("Please try a valid month.")
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
            await ctx.send("Year must be a number.")
    else:
        # use current year
        year = int(EST.strftime("%Y"))
    try:
        date = int(args[1])
    # if date not a number
    except ValueError:
        await ctx.send("Date needs to be a number.")
    try:
        given_date = datetime(year, month, date)
    except ValueError:
        if year > 9999:
            await ctx.send("Year must be less than 10000.")
        else:
            await ctx.send("Date not a valid day for the month.")
    day = given_date.strftime("%A")
    await ctx.send(f"{month}/{date}/{year} is a {day}")


# gives the ice-cream flavors on the menu for today
@client.command()
async def icecream(ctx, *args):
    POSSIBLE_DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    EST = datetime.now(timezone('US/Eastern'))
    TODAY = EST.strftime("%A").upper()
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
            await ctx.send("Error: Not a valid day.")
    # if no day is given
    else:
        # set day to current day
        day = TODAY
    flavors = NUDining.ICE_CREAM_FLAVORS[day]
    await ctx.send(f"There is {flavors} on {day}.")


# stops bot
@client.command()
@commands.has_permissions(administrator=True)
async def logout(ctx):
    await ctx.send("Alright I'll stop now.")
    print(f"{client.user.name} is logging out.")
    await client.logout()


# load cog
@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    try:
        client.load_extension(extension)
        await ctx.send(f"{extension} has been loaded.")
    except Exception as e:
        await ctx.send(f"{extension} was unable to be loaded. [{e}]")


# unload cog
@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    try:
        client.unload_extension(extension)
        await ctx.send(f"{extension} has been unloaded.")
    except Exception as e:
        await ctx.send(f"{extension} was unable to be unloaded. [{e}]")


# loads all extensions
if __name__ == '__main__':
    for extension in EXTENSIONS:
        try:
            client.load_extension(extension)
        except Exception as error:
            print(f"{extension} cannot be loaded. [{error}]")
client.loop.create_task(change_status())  # iniate loop for status
client.run(TOKEN)  # run bot
