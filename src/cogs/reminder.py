import asyncio
import discord
from discord.ext import commands
from typing import Union


class Reminder(commands.Cog):
    """
    Handles anything related to reminders for Discord Members.

    Attributes
    ----------
    client : `commands.Bot`
        a client connection to Discord to interact with the Discord WebSocket and APIs

    Methods
    -------
    reminder(ctx: commands.Context, *args)
        Sends a reminder to a user after a certain amount of time has passed
        with a message of their choice.
    """

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def reminder(self, ctx: commands.Context, *args) -> None:
        """
        Send a reminder to the user after the specified amount of time has passed
        with a message of their choice.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        *args : `tuple`
            A sequence of arguments that the user passes in.
        """
        if ctx.guild is not None:
            await ctx.message.delete()

        if len(args) < 4:
            await ctx.send(
                f"Not enough arguments. Expected at least 4 but got {len(args)}.\n"
                "You need at least reminder content, the word `in`, a number, and a unit of time.\n"
                "Usage: `.reminder <my_reminder> in <number> <unit-of-time>`"
            )
            return
        author: Union[discord.User, discord.Member] = ctx.author
        reminder: str = ""
        original_time: str = args[len(args) - 2]  # user's specified time frame

        # check that the given time is a number
        try:
            time: float = float(original_time)
        except ValueError:
            await self.client.say(
                f"You have to use a number for the 2nd to last term.\n"
                f"Incorrect: `.reminder Husky Bot is cool in five secs`\n"
                f"Correct: `.reminder Husky Bot is cool in 5 secs`"
            )

        UNIT_OF_TIME: str = args[-1].lower()
        SECOND_POSSIBILITIES = {"sec", "secs", "second", "seconds", "s"}
        MINUTE_POSSIBILITIES = {"min", "mins", "minute", "minutes", "m"}
        HOUR_POSSIBILITIES = {"hr", "hrs", "hour", "hours", "h"}
        DAY_POSSIBILITIES = {"day", "days", "d"}
        WEEK_POSSIBILITIES = {"week", "weeks", "w"}
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

        # if the given unit of time was not recognized
        if not valid_unit:
            await ctx.send(
                f"Your unit of measurement must be a second, minute, hour, day, or week.\n"
                f"Incorrect: `.reminder Husky Bot is cool in 1 month`\n"
                f"Correct: `.reminder Husky Bot is cool in 4 weeks`"
            )
            return

        # if the user didn't separate their reminder and unit of time with "in"
        if "in" != args[len(args) - 3]:
            await ctx.send(
                f"You must include the word `in` between your reminder and the time.\n"
                f"Incorrect: `.reminder Husky Bot is cool 5 secs`\n"
                f"Correct: `.reminder Husky Bot is cool in 5 secs`"
            )
            return

        # go through the arguments and add everything before "in" to the reminder string
        for index, value in enumerate(args):
            # once the end of the reminder has been reached break
            if index == len(args) - 3:
                # strip the extra space
                reminder = reminder[-1]
                break
            else:
                reminder += value + " "

        await author.send(
            f"I will remind you about `{reminder}` in `{original_time} {UNIT_OF_TIME}`"
        )
        # wait for specified time in seconds before sending reminder
        await asyncio.sleep(time)
        await author.send(f"Here is your reminder for `{reminder}`")


def setup(client):
    client.add_cog(Reminder(client))
