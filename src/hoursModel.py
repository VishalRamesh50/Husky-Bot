import NUDining
from datetime import datetime
# from datetime import time as t
# from datetime import timedelta as td
from pytz import timezone


class HoursModel:
    """
    A Model which serves as an intermediary
    for processing Location data providing
    providing methods to compare times.

    ...

    Attributes
    ----------
    TODAYS_LOCATIONS : dict
        a dictionary where keys are a tuple of location name aliases
        and values which correspond to LOCATION dictionaries
    CURRENT_LOCATION : dict
        a dictionary where keys are single character day acronyms placed together
        when days have the same value
        and values which correspond to a list of 4 values:
            [opening_hour, opening_min, closing_hour, closing_min]
    EST : timezone
        the python timezone object representing the EST timezone
    TODAY : str
        an completely uppercased string of Today's Day. Ex: 'FRIDAY'

    Methods
    -------
    valid_location(location_name: str)
        Determines whether the given location name is a recognized name
    valid_day(location_name: str)
        Determines whether the given day is a valid day
    """
    def __init__(self):
        # TODO: Assume that the locations are current and no holiday logic exists
        self.TODAYS_LOCATIONS: dict = NUDining.NORMAL_LOCATIONS
        self.CURRENT_LOCATION: dict = {}

        self.EST: timezone = datetime.now(timezone('US/Eastern'))
        self.TODAY: str = self.EST.strftime("%A").upper()
        # self.hour = int(self.EST.strftime("%H"))  # current hour 24hr format
        # self.minute = int(self.EST.strftime("%M"))
        # self.month = int(self.EST.strftime("%m"))
        # self.date = int(self.EST.strftime("%d"))
        # self.year = int(self.EST.strftime("%Y"))
        # self.currDate = datetime(self.year, self.month, self.date)

    def valid_location(self, location_name: str) -> bool:
        """
        Determines whether the given location name is recognized
        as a valid location or an alias of that location from TODAYS_LOCATIONS.
        Also strips whitespace and uppercases the location_name.

        Parameters
        ----------
        location_name : str
            Name of location as a string.

        Returns
        ----------
        True if the given location_name is a valid location else False
        """
        location_name = location_name.upper().strip()
        # TODO: If TODAYS_LOCATIONS was set then ok.
        for key in self.TODAYS_LOCATIONS:
            if location_name in key:
                # TODO: Possibly remove this? Is the method doing more than one thing?
                # Unexpected behavior by assigning a value only after this method is called?
                self.CURRENT_LOCATION = self.TODAYS_LOCATIONS[key]
                return True
        return False

    def valid_day(self, day: str) -> bool:
        """
        Determines whether the given day is a recognized day.
        Also strips whitespace and uppercases the location_name.

        Parameters
        ----------
        day : str
            Name of day as a string.

        Returns
        ----------
        True if the given day is a valid day else False
        """
        VALID_DAYS = {'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'}
        day = day.upper().strip()
        return day in VALID_DAYS
