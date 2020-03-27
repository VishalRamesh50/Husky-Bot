import discord
import logging
import sys
import traceback
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions
from sentry_sdk import capture_exception
from typing import List

from client.setup import client, SENTRY_DSN
from data.ids import ERROR_LOG_CHANNEL_ID
from errors import InvalidChannel

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


@client.event
async def on_error(self, event_method: str, *args, **kwargs) -> None:
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

    logger.warning(f"Some error with {event_method}!")
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
    if SENTRY_DSN:
        capture_exception(error)


@client.event
async def on_command_error(
    self, ctx: commands.Context, error: commands.CommandError
) -> None:
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

    logger.warning(f"There was some error thrown on command {ctx.command}")
    # try to get the original error if one exists
    og_cause = error.__cause__
    if og_cause:
        error = og_cause

    errors: List[discord.DiscordException] = [error]

    if issubclass(type(error), commands.CheckFailure):
        if isinstance(error, commands.CheckAnyFailure):
            errors += error.errors

        e: List[InvalidChannel] = [e for e in errors if isinstance(e, InvalidChannel)]
        if e:
            await ctx.send(
                f"Not here! Try again in {e[0].missing_channel}", delete_after=5
            )
            return
        missing_perm_errors: List[MissingPermissions] = [
            e for e in errors if isinstance(e, MissingPermissions)
        ]
        if missing_perm_errors:
            missing: List[str] = []
            for err in missing_perm_errors:
                missing += err.missing_perms
            error = MissingPermissions(missing)
            await ctx.send(
                str(error).replace(" and ", " or "), delete_after=5,
            )
            return

    elif isinstance(error, commands.CommandNotFound):
        # if the prefix is in the error it probably wasn't meant to be a command
        if self.client.command_prefix in str(error):
            return

    # add the error onto the kwargs for the on_error to have access
    ctx.kwargs["thrown_error"] = error
    ctx.kwargs["thrown_guild"] = ctx.guild
    await self.client.on_error(ctx.command, *ctx.args, **ctx.kwargs)
