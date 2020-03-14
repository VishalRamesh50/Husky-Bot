import calendar
from data import nu_dining
from datetime import datetime
from discord.ext import commands
from pytz import timezone
from typing import List, Optional


class IceCream(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def icecream(self, ctx: commands.Context, day: Optional[str] = None) -> None:
        """Gives the ice-cream flavors on the menu for the given day.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        day: `str`
            The day to find icecream flavors for.
        """

        POSSIBLE_DAYS: List[str] = [d.upper() for d in calendar.day_name]
        EST = datetime.now(timezone("US/Eastern"))
        TODAY = EST.strftime("%A").upper()
        if day is None:
            day = TODAY
        day = day.strip().upper()
        if day in POSSIBLE_DAYS:
            pass
        elif day in "TOMORROW":
            day = POSSIBLE_DAYS[(POSSIBLE_DAYS.index(TODAY) + 1) % len(POSSIBLE_DAYS)]
        else:
            await ctx.send("Error: Not a valid day.")
            return
        flavors = nu_dining.ICE_CREAM_FLAVORS[day]
        await ctx.send(f"There is {flavors} on {day}.")


def setup(client: commands.Bot):
    client.add_cog(IceCream(client))
