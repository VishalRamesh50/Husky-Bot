import asyncio
import discord
import logging
import os
from checks import is_admin, is_mod
from discord.ext import commands, tasks
from dotenv import load_dotenv
from itertools import cycle
from typing import Dict

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
    "error_handler",
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

COGS_DIRECTORY = "cogs"
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


# stops bot
@client.command()
@commands.has_permissions(administrator=True)
async def logout(ctx):
    await ctx.send("Alright I'll stop now.")
    logging.info(f"{client.user.name} is logging out.")
    await client.logout()


@is_admin()
@client.command()
async def load(ctx: commands.Context, extension: str) -> None:
    """Loads the given extension."""
    try:
        client.load_extension(f"{COGS_DIRECTORY}.{extension}")
        await ctx.send(f"{extension} has been loaded.")
    except Exception as e:
        await ctx.send(f"{extension} was unable to be loaded. [{e}]")


@is_admin()
@client.command()
async def unload(ctx: commands.Context, extension: str) -> None:
    """Unloads the given extension."""
    try:
        client.unload_extension(f"{COGS_DIRECTORY}.{extension}")
        await ctx.send(f"{extension} has been unloaded.")
    except Exception as e:
        await ctx.send(f"{extension} was unable to be unloaded. [{e}]")


if __name__ == "__main__":
    # loads all extensions
    for extension in EXTENSIONS:
        try:
            client.load_extension(f"{COGS_DIRECTORY}.{extension}")
        except Exception as error:
            logger.warning(f"{extension} cannot be loaded. [{error}]")
    # create event to cycle through presences
    change_status.start()
    # start bot
    client.run(os.environ["TOKEN"])
