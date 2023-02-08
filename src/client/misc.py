import asyncio
import discord
import logging
from discord.ext import commands, tasks
from itertools import cycle

from client.setup import client, PREFIX
from checks import is_admin

logger = logging.getLogger(__name__)


@client.event
async def on_ready():
    """Bot is ready."""
    logger.info(f"{client.user.name} is ONLINE!")


@tasks.loop()
async def change_status() -> None:
    """Cycles through the bot presences every 5 seconds."""

    STATUS = ["With Huskies!", f"{PREFIX}help", f"{PREFIX}ticket"]
    msgs = cycle(STATUS)

    await client.wait_until_ready()

    while not client.is_closed():
        current_status = next(msgs)
        await client.change_presence(activity=discord.Game(current_status))
        await asyncio.sleep(5)


@is_admin()
@client.command()
async def logout(ctx: commands.Context) -> None:
    """Logs the client out, stopping the bot.

    Parameters
    ------------
    ctx: `commands.Context`
        A class containing metadata about the command invocation.
    """
    await ctx.send("Alright I'll stop now.")
    await client.close()
    logger.info(f"{client.user.name} has logged out.")
