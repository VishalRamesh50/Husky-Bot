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

from data.ids import (
    BOT_SPAM_CHANNEL_ID,
    COURSE_REGISTRATION_CHANNEL_ID,
    ERROR_LOG_CHANNEL_ID,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EXTENSIONS = [
    "activity",
    "aoun",
    "april_fools",
    "clear",
    "course_registration",
    "day",
    "help",
    "hours.hours",
    "icecream",
    "it_be_like_that",
    "logs",
    "misc",
    "onboarding",
    "reaction",
    "reminder",
    "schedules",
    "stats",
    "twitch",
]

PREFIX = os.environ.get("PREFIX", ".")
client = commands.Bot(command_prefix=PREFIX)  # bot prefix
client.remove_command("help")  # remove default help command


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
    tb_content = "".join(extracted_tb.format())

    # Notify of exception
    embed = discord.Embed(
        title=f"{error.__class__.__name__} {str(error)}",
        timestamp=datetime.utcnow(),
        description=f"```{tb_content}```" if tb_content else "",
        colour=discord.Colour.red(),
    )

    embed.set_author(name=f"Command/Event: {event_method}")
    embed.set_footer(text=kwargs.get("thrown_guild", "Unknown Guild"))

    for arg in args:
        arg_name = str(arg) or '""'
        if arg_name.startswith("<") and "." in arg_name:
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
    set a keyword `thrown_error` and `guild` on the kwargs called with on_error.

    Parameters
    ------------
    ctx: `commands.Context`
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
        if str(error) == "The check functions for command choose failed.":
            await ctx.message.delete()
            await ctx.send(
                f"Not here! Try again in {COURSE_REGISTRATION_CHANNEL.mention}",
                delete_after=5,
            )
            return
        # -------------------------------------------------------------------------

        # --------------------------- BOT-SPAM CHECK ------------------------------
        BOT_SPAM_CHANNEL = client.get_channel(BOT_SPAM_CHANNEL_ID)
        bot_spam_necessary_commands = ["hours", "open", "ping", "whois"]
        for command in bot_spam_necessary_commands:
            if str(error) == f"The check functions for command {command} failed.":
                await ctx.message.delete()
                await ctx.send(
                    f"Not here! Try again in {BOT_SPAM_CHANNEL.mention}", delete_after=5
                )
                return
        # -------------------------------------------------------------------------
    elif isinstance(error, commands.CommandNotFound):
        # if the prefix is in the error it probably wasn't meant to be a command
        if PREFIX in str(error):
            return
    # add the error onto the kwargs for the on_error to have access
    ctx.kwargs["thrown_error"] = error
    ctx.kwargs["thrown_guild"] = ctx.guild
    await on_error(ctx.command, *ctx.args, **ctx.kwargs)


# disable DM commands
@client.check
async def guild_only(ctx):
    return ctx.guild is not None


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


if __name__ == "__main__":
    # loads all extensions
    for extension in EXTENSIONS:
        try:
            client.load_extension(f"cogs.{extension}")
        except Exception as error:
            logger.warning(f"{extension} cannot be loaded. [{error}]")
    # create event to cycle through presences
    change_status.start()
    # start bot
    client.run(os.environ["TOKEN"])
