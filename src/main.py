import asyncio
import discord
import logging
import os
import sys
import traceback
from datetime import datetime
from discord.ext import commands, tasks
from dotenv import load_dotenv
from itertools import cycle
from pytz import timezone

from cogs.hours import nu_dining
from ids import (
    BOT_SPAM_CHANNEL_ID,
    COURSE_REGISTRATION_CHANNEL_ID,
    ERROR_LOG_CHANNEL_ID,
    SUGGESTIONS_CHANNEL_ID,
    V_MONEY_ID,
)

load_dotenv()
TOKEN = os.environ["TOKEN"]  # secret Bot TOKEN
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EXTENSIONS = ['activity', 'aoun', 'april_fools', 'course_registration', 'help',
              'hours.hours', 'it_be_like_that', 'logs', 'misc', 'onboarding',
              'reaction', 'reminder', 'schedules', 'stats', 'twitch']

PREFIX = "."
client = commands.Bot(command_prefix=PREFIX)  # bot prefix
client.remove_command('help')  # remove default help command


@client.event  # Bot is Ready
async def on_ready():
    print(f"{client.user.name} is ONLINE!")


@tasks.loop()
async def change_status() -> None:
    """Cycles through the bot presences every 5 seconds."""

    STATUS = ["With Huskies!", f"{PREFIX}help"]
    msgs = cycle(STATUS)

    await client.wait_until_ready()

    while not client.is_closed():
        current_status = next(msgs)
        await client.change_presence(activity=discord.Game(current_status))
        await asyncio.sleep(5)


@client.event
async def on_error(event_method: str, *args, **kwargs) -> None:
    """Global error handler to catch all errors thrown.

    Will send an embedded message in the #error-log channel.
    Includes traceback, Exception name, args, guild, and timestamp.

    Parameters
    ------------
    event_method: `str`
        The method which the exception was thrown in.
    *args:
        The arguments the method was called with.
    **kwargs:
        The keyword arguments the method was called with.
    """

    logger.error(f"Some error with {event_method}!")
    ERROR_LOG_CHANNEL: discord.TextChannel = client.get_channel(ERROR_LOG_CHANNEL_ID)
    err_type, error, tb = sys.exc_info()

    if error is None:
        # custom error added when coming from on_command_error
        error = kwargs.get("thrown_error")
        if error is None:
            return

    og_cause = error.__cause__
    if og_cause:
        error = og_cause

    tb = error.__traceback__
    extracted_tb = traceback.extract_tb(tb)
    tb_content = ''.join(extracted_tb.format())

    # Notify of exception
    embed = discord.Embed(
        title=f"{error.__class__.__name__} {str(error)}",
        timestamp=datetime.utcnow(),
        description=f"```{tb_content}```" if tb_content else '',
        colour=discord.Colour.red())

    embed.set_author(name=f"Command/Event: {event_method}")

    for arg in args:
        arg_name = str(arg) or '""'
        if arg_name.startswith("<") and '.' in arg_name:
            arg_type = arg.__class__.__name__
        else:
            arg_type = type(arg)
        embed.add_field(name=arg_type, value=arg_name, inline=True)

        # if there is the guild property on this arg
        if "guild" in dir(arg):
            embed.set_footer(text=f"Guild: {arg.guild}")

    await ERROR_LOG_CHANNEL.send(embed=embed)
    traceback.print_exception(err_type, error, tb)


# error handler
@client.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    """Global command_error handler to catch all errors thrown.

    Some logic to ignore certain exceptions and gracefully redirect is in here.
    If no recognized error can be ignored it will be sent to the on_error and
    set a keyword thrown_error on the kwargs called with on_error.

    Parameters
    ------------
    ctx: `ctx`
        A class containing metadata about the command invocation.
    error: `commands.CommandError`
        The exception which triggered the calling of this method.
    """

    # try to get the original error if one exists
    og_cause = error.__cause__
    if og_cause:
        error = og_cause

    if isinstance(error, commands.CheckFailure):
        # ----------------------- COURSE-REGSISTRATION CHECK ----------------------
        COURSE_REGISTRATION_CHANNEL = client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        if (str(error) == "The check functions for command choose failed."):
            await ctx.message.delete()
            await ctx.send("Not here! Try again in" + COURSE_REGISTRATION_CHANNEL.mention, delete_after=5)
            return
        # -------------------------------------------------------------------------

        # --------------------------- BOT-SPAM CHECK ------------------------------
        BOT_SPAM_CHANNEL = client.get_channel(BOT_SPAM_CHANNEL_ID)
        bot_spam_necessary_commands = ['ping', 'whois', 'hours', 'open']
        for command in bot_spam_necessary_commands:
            if (str(error) == f"The check functions for command {command} failed."):
                await ctx.message.delete()
                await ctx.send("Not here! Try again in" + BOT_SPAM_CHANNEL.mention, delete_after=5)
                return
        # -------------------------------------------------------------------------
    elif isinstance(error, commands.CommandNotFound):
        # if the prefix is in the error it probably wasn't meant to be a command
        if PREFIX in str(error):
            return
    # add the error onto the kwargs for the on_error to have access
    ctx.kwargs["thrown_error"] = error
    await on_error(ctx.command, *ctx.args, **ctx.kwargs)


# disable DM commands
@client.check
async def guild_only(ctx):
    return ctx.guild is not None


# deletes set amount of messages
@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=1, member: discord.Member = None):
    amount = int(amount)
    channel = ctx.channel
    await ctx.message.delete()  # deletes command
    if amount <= 0:
        await ctx.send("Cannot delete less than 1 message.")
    else:
        # if a member was not chosen
        if member is None:
            deleted_messages = await channel.purge(limit=amount)
            if (amount > 1000):
                await ctx.send("Cannot delete more than 1000 messages at a time.")
                return
        # if a specific member was chosen
        else:
            if amount > 100:
                await ctx.send("Cannot delete more than 100 messages when a member is mentioned.")
                return
            counter = 0
            deleted_messages = []
            async for message in channel.history(limit=None):
                if counter > amount:
                    break
                if message.author == member:
                    deleted_messages.append(message)
                    counter += 1
            await channel.delete_messages(deleted_messages)
        await ctx.send(f"{len(deleted_messages)} messages deleted.", delete_after=5)


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
            day = POSSIBLE_DAYS[(POSSIBLE_DAYS.index(TODAY) + 1) % len(POSSIBLE_DAYS)]
        # if not a valid day
        else:
            await ctx.send("Error: Not a valid day.")
    # if no day is given
    else:
        # set day to current day
        day = TODAY
    flavors = nu_dining.ICE_CREAM_FLAVORS[day]
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


if __name__ == '__main__':
    # loads all extensions
    for extension in EXTENSIONS:
        try:
            client.load_extension(f"cogs.{extension}")
        except Exception as error:
            logger.warning(f"{extension} cannot be loaded. [{error}]")
    # create event to cycle through presences
    change_status.start()
    # start bot
    client.run(TOKEN)
