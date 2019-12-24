import discord
from discord.ext import commands
from hours_model import HoursModel
from typing import Tuple

BOT_SPAM_CHANNEL_ID = 531665740521144341


class Hours(commands.Cog):
    """
    An interface to provide information to users related
    to hours of operation for select locations.

    Attributes
    ----------
    client : discord.Client
        a client connection to Discord to interact with the Discord WebSocket and APIs
    model : HoursModel
        a model which aids this module in processing of data and giving usable information
    BUFFER_TIME : int
        the limit between informing users that the given location is about to close or open

    Methods
    -------
    hours(ctx: commands.Context, *args)
        Takes in arguments in the form of <location> [,<day>]
        and determines whether the location is open or not with additional info.
    open(ctx: commands.Context)
        Gives an embedded message full of open locations at the current time.
    """
    def __init__(self, client: discord.Client):
        self.client = client
        self.model = HoursModel()
        self.BUFFER_TIME = 60

    def __clean_input(self, input: str) -> str:
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
    async def hours(self, ctx: commands.Context , *args) -> None:
        """
        Gives the hours of operation for select locations
        and determines whether open or not.

        Parameters
        ----------
        *args : `tuple`
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
        day: str = self.__clean_input(day)
        location: str = self.__clean_input(location)

        # Currently the function cleans up the input as well
        valid_location: bool = self.model.valid_location(location)
        valid_day: bool = self.model.valid_day(day)

        # ----------------------------- User Input Handling -------------------------
        AVAILABLE_LOCATIONS: str = self.model.get_available_locations()
        AVAILABLE_LOCATIONS_MSG: str = f"**__Here's a list of available locations (A-Z):__**\n{AVAILABLE_LOCATIONS}"
        if location == '':
            await ctx.send('A `location` must be given.')
            await ctx.send(f"{AVAILABLE_LOCATIONS_MSG}\n*This will be deleted in 15 seconds.*", delete_after=15)
            await ctx.author.send(AVAILABLE_LOCATIONS_MSG)
            return
        # if a comma was used
        if comma:
            # if no valid location given
            if not valid_location:
                await ctx.send(f"Location: `{location}` not recognized.")
                await ctx.send(f"{AVAILABLE_LOCATIONS_MSG}\n*This will be deleted in 15 seconds.*", delete_after=15)
                await ctx.author.send(AVAILABLE_LOCATIONS_MSG)
                return
            # if no day given
            elif day == '':
                await ctx.send('A `day` must be given if a comma is provided.')
                return
            # if no valid day given
            elif not valid_day:
                await ctx.send(f"Day: `{day}` not recognized.")
                return
        # if no comma was used
        else:
            # if no valid location recognized
            if not valid_location:
                await ctx.send(f"Location: `{location}` was not recognized. "
                            "Please use a comma to separate location and day "
                            "or enter a valid location.")
                await ctx.send(f"{AVAILABLE_LOCATIONS_MSG}\n*This will be deleted in 15 seconds.*", delete_after=15)
                await ctx.author.send(AVAILABLE_LOCATIONS_MSG)
                return
            # if location recognized but no day provided, use today's day
            else:
                day = self.model.get_today()
        # ---------------------------------------------------------------------------

        location_hours_msg: str = self.model.location_hours_msg(location, day)
        msg: str = ""  # the final message which the user will receive
        # if the user is trying to see if the location is currently open
        if day == self.model.get_today():
            # if function has not exited yet then there were no errors with user input
            if (self.model.is_open(location, day)):
                msg += f"{location} is OPEN now! {location_hours_msg}. "
                time_till_closing: int = self.model.time_till_closing(location, day)
                # if the location is closing within the BUFFER_TIME
                if (0 < time_till_closing <= self.BUFFER_TIME):
                    msg += f"It will be closing in {time_till_closing} mins!"
            else:
                # if the location is closed all day
                if self.model.closed_all_day(location, day):
                    msg += location_hours_msg + '.'
                # if the location is just closed at the current time
                else:
                    msg += f"{location} is CLOSED now. {location_hours_msg}. "
                    time_till_open: int = self.model.time_till_open(location, day)
                    # if the location is opening within the BUFFER_TIME
                    if (0 < time_till_open <= self.BUFFER_TIME):
                        msg += f"It will be opening in {time_till_open} mins!"
        # if the user wants to see the hours for another day
        else:
            msg += location_hours_msg + '.'
        link: str = self.model.get_link(location, day)
        await ctx.send(msg + '\n' + link)

    # gives a list of all the open locations
    @commands.command()
    async def open(self, ctx):
        pass


def setup(client):
    client.add_cog(Hours(client))
