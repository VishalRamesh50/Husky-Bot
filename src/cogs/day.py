import re
from datetime import datetime
from discord.ext import commands
from pytz import timezone
from typing import Optional


class Day(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def day(self, ctx: commands.Context, *args):
        """Tells what day of the week the given date is.

        Recognized Formats:
            - mm/dd/yy
            - mm/dd/YYYY
            - Month dd, YY
            - MonthAcronym dd, YY
        Whitespace does not matter.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation
        args:
            The date format being sent by the user.
        """

        EST = datetime.now(timezone("US/Eastern"))
        given_date: str = ""
        for arg in args:
            given_date += arg.strip()

        recognized_format = ["%m/%d/%y", "%m/%d/%Y", "%B%d,%Y", "%b%d,%Y"]
        valid_datetime: Optional[datetime] = None
        for date_format in recognized_format:
            try:
                valid_datetime = datetime.strptime(given_date, date_format)
            except ValueError:
                try:
                    # if year was not given use the current year
                    if "Y" in date_format.upper():
                        date_format = re.sub("[/,]%[yY]", "", date_format)
                        valid_datetime = datetime.strptime(given_date, date_format)
                        valid_datetime = datetime(
                            EST.year, valid_datetime.month, valid_datetime.day
                        )
                    break
                except ValueError:
                    pass
        if valid_datetime is None:
            await ctx.send(
                "The date sent was not in a recognizable format.", delete_after=5
            )
            await ctx.author.send(
                "Recognized Formats:\n"
                "- mm/dd/yy\n"
                "- mm/dd/YYYY\n"
                "- Month dd, YY\n"
                "- MonthAcronym dd, YY"
            )
            return
        day: str = valid_datetime.strftime("%A")
        month, date, year = (
            valid_datetime.month,
            valid_datetime.day,
            valid_datetime.year,
        )
        await ctx.send(f"{month}/{date}/{year} is a {day}")


def setup(client: commands.Bot):
    client.add_cog(Day(client))
