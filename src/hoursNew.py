from discord.ext import commands
from hoursModel import HoursModel
from typing import Tuple

BOT_SPAM_CHANNEL_ID = 531665740521144341


class Hours(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.model = HoursModel()
        self.BUFFER_TIME = 60

    def clean_input(self, input: str) -> str:
        return input.upper().strip()

    # separates location and day by comma
    def __parse_comma(self, args: Tuple[str]) -> Tuple[str, bool, str]:
        """
        Parses a list of arguments, determines if a comma exists,
        and then sets the day to be the string after the comma,
        and location to be the string before the comma.
        Also strips whitespace and uppercases the arguments.
        Return order is day, comma, location.

        Parameters
        ----------
        args : tuple
            Tuple of arguments as strings

        Returns
        ----------
        A tuple of (day, comma, location)
        """

        day: str = ""  # user-input day
        comma: bool = False  # if a comma existed in the user input
        location: str = ""  # the location that the user entered (excluding the day if given)

        args = ' '.join(args).split(',')
        # if a comma existed
        if len(args) > 1:
            day = args[1].upper().strip()
            comma = True
        location = args[0].upper().strip()
        return day, comma, location

    @commands.command()
    async def hours(self, ctx, *args) -> None:
        """
        Gives the hours of operation for select locations
        and determines whether open or not.

        Parameters
        ----------
        *args : tuple
            List of arguments the user passes in

        Returns
        ----------
        None
        """
        day: str  # user-input day
        comma: bool  # if a comma existed in the user input
        location: str  # the location that the user entered (excluding the day if given)
        day, comma, location = self.__parse_comma(args)

        # TODO: choice to either clean up input before checking or do this during function
        day: str = self.clean_input(day)
        location: str = self.clean_input(location)

        # Currently the function cleans up the input as well
        valid_location: bool = self.model.valid_location(location)
        valid_day: bool = self.model.valid_day(day)

        # ----------------------------- User Input Handling -------------------------
        if comma:
            if not valid_location:
                await ctx.send(f"Location: `{location}` not recognized.")
                # TODO: Send a message to the user of doc/link/list of valid locations here
                return
            if not valid_day:
                await ctx.send(f"Day: `{day}` not recognized.")
                return
        else:
            if not valid_location:
                await ctx.send(f"Location: `{location}` was not recognized. "
                               "Please use a comma to separate location and day "
                               "or enter a valid location.")
                # TODO: Send a message to the user of doc/link/list of valid locations here
                return
        # ---------------------------------------------------------------------------

        # if function has not exited yet then there were no errors with user input
        location_hours_msg: str = self.model.location_hours_msg(location, day)
        if (self.model.open(location, day)):
            time_till_closing: int = self.model.time_till_closing(location, day)
            if (time_till_closing <= self.BUFFER_TIME):
                await ctx.send(f"{location} is OPEN now! {location_hours_msg}. "
                               f"It will be closing in {time_till_closing} mins!")
        else:
            time_till_open: int = self.model.time_till_open(location, day)
            if (time_till_open <= self.BUFFER_TIME):
                await ctx.send(f"{location} is CLOSED now. {location_hours_msg}. "
                               f"It will be opening in {time_till_open} mins!")

    # gives a list of all the open locations
    @commands.command()
    async def open(self, ctx):
        pass


def setup(client):
    client.add_cog(Hours(client))
