import nu_dining
from datetime import datetime, timedelta as td
from pytz import timezone
from typing import Tuple, List, Dict


class HoursModel:
    """
    A Model which serves as an intermediary
    for processing Location data providing
    providing methods to compare times.

    Attributes
    ----------
    todays_locations : dict
        a dictionary where keys are a tuple of location name aliases
        and values which correspond to LOCATION dictionaries
    current_location : dict
        a dictionary where keys are single character day acronyms placed together
        when days have the same value
        and values which correspond to a list of 4 values:
            [opening_hour, opening_min, closing_hour, closing_min]
    ORDERED_DAYS: list
        A list of the days of the week in order from Sunday-Saturday all uppercased
    VALID_DAYS: set
        A set of uppercased strings which indicate a valid day
    DAYS_TO_ACRONYMS: dict
        A dict where the keys are valid days and the values are the corresponding acronyms
    ACRONYMS_TO_DATE: dict
        The reverse of DAYS_TO_ACRONYMS where the keys are the acronyms and the values are a valid day
    est : datetime
        the python datetime object representing the current time in the US/Eastern timezone
    today : str
        an uppercased string of Today's Day. Ex: 'FRIDAY'

    Methods
    -------
    valid_location(location_name: str) -> bool
        Determines whether the given location name is a recognized name.
    valid_day(location_name: str) -> bool
        Determines whether the given day is a recognized day.
    location_hours_msg(location: str, day: str) -> str
        Returns a string representing the hours of operation
        for the given location on the given day.
    is_open(location: str, day: str) -> bool
        Determines whether the given location is open on the given day
    time_till_open(location: str, day: str) -> float
        Figures out the time in minutes until the given location
        will be open on a given day.
    time_till_closing(location: str, day: str) -> float
        Figures out the time in minutes until the given location
        will be closed on a given day.
    get_today() -> str
        Gets today's day as an uppercased string.
    """
    def __init__(self):
        # TODO: Assume that the locations are current and no holiday logic exists
        # ------------------------------ VARIABLES --------------------------------
        self.todays_locations: Dict[Tuple[str], dict] = nu_dining.NORMAL_LOCATIONS
        self.current_location: dict = {}
        # ------------------------------ CONSTANTS --------------------------------
        self.ORDERED_DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        self.VALID_DAYS = {'SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'}
        self.DAYS_TO_ACRONYMS: dict = {'SUNDAY': 'U', 'MONDAY': 'M', 'TUESDAY': 'T', 'WEDNESDAY': 'W',
                                       'THURSDAY': 'R', 'FRIDAY': 'F', 'SATURDAY': 'S'}
        self.ACRONYMS_TO_DAYS: dict = dict([(value, key) for key, value in self.DAYS_TO_ACRONYMS.items()])
        # ---------------------------- TIME VARIABLES -----------------------------
        self.est: datetime = datetime.now(timezone('US/Eastern'))
        self.today: str = self.est.strftime("%A").upper()

    def __reset_time(self):
        self.est: datetime = datetime.now(timezone('US/Eastern'))
        self.today: str = self.est.strftime("%A").upper()

    # TODO: Find a way to keep this from being duplicated since it's common in many classes
    # Possibly create a decorator or make it a function in a Utils class
    def __clean_input(self, input: str) -> str:
        return input.strip().upper()

    def __set_todays_location(self) -> None:
        """Sets self.todays_location based on today's date."""
        self.__reset_time()
        today_datetime: datetime = datetime(self.est.year, self.est.month, self.est.day)
        for date, location in nu_dining.DATES_TO_LOCATIONS.items():
            start_date: str  # start date in the format mm/dd/yy
            end_date: str  # end date in the format mm/dd/yy
            # date has the format mm/dd/yy-mm/dd/yy
            start_date, end_date = date.split('-')
            start_datetime: datetime = datetime.strptime(start_date, '%m/%d/%y')
            end_datetime: datetime = datetime.strptime(end_date, '%m/%d/%y')
            # if today's date is within the range of these ranges
            if start_datetime <= today_datetime <= end_datetime:
                self.todays_locations = location
                return
        self.todays_locations = nu_dining.NORMAL_LOCATIONS


    def valid_location(self, location_name: str) -> bool:
        """
        Determines whether the given location name is recognized
        as a valid location or an alias of that location from todays_locations.
        Also strips whitespace and uppercases the location_name.

        Note: Sets the current_location to be the valid location data structure
        if location_name is valid. (This is a side-effect)

        Parameters
        ----------
        location_name : str
            Name of location as a string.

        Returns
        ----------
        True if the given location_name is a valid location else False
        """
        self.__set_todays_location()
        location_name: str = self.__clean_input(location_name)
        for aliases, location in self.todays_locations.items():
            if location_name in aliases:
                # TODO: Possibly remove this? Is the method doing more than one thing?
                # Unexpected behavior by assigning a value only after this method is called?
                self.current_location = location
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
        day = self.__clean_input(day)
        return day in self.VALID_DAYS

    def __obtain_hours_key_value(self, location, day) -> Tuple[str, List[int]]:
        """
        Searches through the location dictionaries for the current_location
        and then returns the key value pair for the given location which contains
        the range for the given day.

        Parameters
        ----------
        location: str
            Name of locations as a string.
        day : str
            Name of day as a string.

        Returns
        ----------
        Tuple of a String and a List of integers (of length 4)
        Ex: ('MTWR', [11, 0, 20, 0])
        List of integers will be of value -1 if the location is closed the entire day.
        Ex: ('U', [-1, -1, -1, -1])

        Raises
        ----------
        AssertionError: If the given location/day is not a valid location/day.
        """
        # confirm that the given location is a valid and sets the current_location
        assert(self.valid_location(location))
        # confirm that the given day is valid
        assert(self.valid_day(day))
        day = self.__clean_input(day)
        day_acronym = self.DAYS_TO_ACRONYMS[day]
        # for each key (which is a string of day acronyms) in the dict of current_location
        for k in self.current_location:
            # if the acronym version of the given day is in the key
            # then the range is correct, so return the key, value pair
            if day_acronym in k:
                return k, self.current_location[k]
        # if the location is closed for the given day
        return day_acronym, [-1, -1, -1, -1]

    def __obtain_times(self, key_value_pair: Tuple[str, List[int]]) -> List[int]:
        """
        Given a key value pair of day range to time as a tuple,
        will return just the time as a list of ints.

        Parameters
        ----------
        key_value_pair: Tuple[str, List[int]]
            A tuple where the first value is a string representing the day range
            and the second value is a list of 4 integers where each int corresponds
            to an hour, min, hour, min respectively.
            Ex: ('MTWR', [11, 0, 20, 0])

        Returns
        ----------
        A list of 4 integers representing the time
        Ex: [11, 0, 20, 0]
        List may be of 4 integers with value -1 if the location is closed the entire day
        Ex: [-1, -1, -1, -1]

        Raises
        ----------
        AssertionError: If the length of the time list is not 4
        """
        result = key_value_pair[1]
        assert len(result) == 4, "Length of time list must be 4"
        return result

    def __obtain_day_range(self, key_value_pair: Tuple[str, List[int]]) -> str:
        """
        Given a key value pair of day range to time as a tuple,
        will return just the day range as a string.

        Parameters
        ----------
        key_value_pair: Tuple[str, List[int]]
            A tuple where the first value is a string representing the day range
            and the second value is a list of 4 integers where each int corresponds
            to an hour, min, hour, min respectively.
            Ex: ('MTWR', [11, 0, 20, 0])

        Returns
        ----------
        A string representing the starting day to ending day in the format:
        "STARTING_DAY-ENDING_DAY"

        Raises
        ----------
        AssertionError: If the day_range does not have at least 1 character.
        """
        # the day range is the first value in the key value pair
        day_range = key_value_pair[0]
        day_range = self.__clean_input(day_range)
        # make sure that the day value has at least 1 character
        assert(len(day_range) > 0)
        # if the day range is only one character
        if len(day_range) == 1:
            # convert the single character to a full day name
            return self.ACRONYMS_TO_DAYS[day_range]
        # if the day range is more than one character
        else:
            first_day = self.ACRONYMS_TO_DAYS[day_range[0]]
            last_day = self.ACRONYMS_TO_DAYS[day_range[-1]]
            return first_day + '-' + last_day

    def __determine_period(self, hour: int) -> str:
        """
        Determines whether given a time in hours is
        'AM' or 'PM'

        Parameters
        ----------
        hour: int
            Number of hours (in 24 time) as an integer.

        Returns
        ----------
        'AM' if the time when fitted into a day is in the morning else 'PM'
        Ex: 25 -> 'AM' or 13 -> 'PM'

        Raises
        ----------
        AssertionError: If the given hour is not positive.
        """
        assert hour >= 0, 'Given hour must be positive'
        # convert hour into a 24 hour time
        hour = hour % 24
        # return AM if morning else PM
        return 'AM' if hour < 12 else 'PM'

    def location_hours_msg(self, location: str, day: str) -> str:
        """
        Returns a string representing the hours of operation
        for the given location on the given day.

        Parameters
        ----------
        location : str
            Name of location as a string.
        day : str
            Name of day as a string.

        Returns
        ----------
        String of the format:
        <location> is open from <opening_time> - <closing_time> on <day>
        Ex: STETSON WEST is open from 4:00pm - 8:00pm on SUNDAY
        or
        <location> is CLOSED <days>
        Ex: STETSON WEST is CLOSED SATURDAY
        """
        location = self.__clean_input(location)
        day = self.__clean_input(day)
        key_value_pair: Tuple[str, List[int]] = self.__obtain_hours_key_value(location, day)
        opening_hour, opening_min, closing_hour, closing_min = self.__obtain_times(key_value_pair)
        days = self.__obtain_day_range(key_value_pair)
        # if the location has sentinel values with all -1 times, it's closed that entire day
        if opening_hour == opening_min == closing_hour == closing_min == -1:
            return f"{location} is CLOSED {days}"
        # determine periods for opening and closing (AM/PM)
        opening_period = self.__determine_period(opening_hour)
        closing_period = self.__determine_period(closing_hour)
        # convert opening/closing hours to 12hr time
        opening_hour %= 12
        closing_hour %= 12
        # pad opening/closing mins with 0 if single digit
        opening_min = str(opening_min).zfill(2)
        closing_min = str(closing_min).zfill(2)
        result = (f"{location} is open from "
                  f"{opening_hour}:{opening_min} {opening_period} - "
                  f"{closing_hour}:{closing_min} {closing_period} "
                  f"on {days}")
        return result

    def __get_yesterday(self, day: str) -> str:
        """
        Gets the day before the given day.

        Parameters
        ----------
        day : str
            Name of day as a string.

        Returns
        ----------
        A string representing the day before the given day in all caps.
        """
        assert(self.valid_day(day))
        #TODO: This will not work if valid days support acronyms
        curr_index: int = self.ORDERED_DAYS.index(day)
        return self.ORDERED_DAYS[(curr_index - 1) % len(self.ORDERED_DAYS)]

    def __convert_to_datetime(self, hours: int, mins: int, day: str) -> datetime:
        """
        Creates a datetime object out of the given hours and minutes at the given day
        relative to today's current time and date.

        Parameters
        ----------
        hours : int
            time in hours (must be positive)
        mins: int
            time in minutes (must be between 0 and 60 [0,60))
        day : str
            Name of day as a string

        Returns
        ----------
        True if the location is open else False.

        Raises
        ----------
        AssertionError: if hours is negative, mins is not within 0 to 60 [0,60),
        or day is not valid
        """
        assert(hours >= 0)
        assert(0 <= mins < 60)
        assert(self.valid_day(day))
        self.__reset_time()
        day = self.__clean_input(day)
        diff_of_days: int = hours // 24
        remaining_hours: int = hours % 24
        # print(f'Day:{day}, Hours:{hours}, DiffDays: {diff_of_days}')
        index_of_curr_day: int = self.ORDERED_DAYS.index(self.today)
        while(True):
            # if yesterday is the given day
            if self.__get_yesterday(self.ORDERED_DAYS[index_of_curr_day]) == day:
                diff_of_days -= 1
                break
            elif self.ORDERED_DAYS[index_of_curr_day] == day:
                break
            index_of_curr_day = (1 + index_of_curr_day) % len(self.ORDERED_DAYS)
            diff_of_days += 1
        result = datetime(self.est.year, self.est.month, self.est.day, remaining_hours, mins)
        return result + td(days=diff_of_days)

    def is_open(self, location: str, day: str) -> bool:
        """
        Determines whether the given location is open on the given day
        at the current time.

        Parameters
        ----------
        location : str
            Name of location as a string.
        day : str
            Name of day as a string.

        Returns
        ----------
        True if the location is open else False.
        """
        key_value_pair: Tuple[str, List[int]] = self.__obtain_hours_key_value(location, day)
        opening_hour, opening_min, closing_hour, closing_min = self.__obtain_times(key_value_pair)
        # if it's closed the entire day
        if opening_hour == opening_min == closing_hour == closing_min == -1:
            return False
        opening_time: datetime = self.__convert_to_datetime(opening_hour, opening_min, day)
        closing_time: datetime = self.__convert_to_datetime(closing_hour, closing_min, day)
        current_time: datetime = self.__convert_to_datetime(self.est.hour, self.est.minute, self.today)
        # --------------------------------- YESTERDAY -----------------------------
        yesterday: str = self.__get_yesterday(day)
        ykey_value_pair: Tuple[str, List[int]] = self.__obtain_hours_key_value(location, yesterday)
        *_, yclosing_hour, yclosing_min = self.__obtain_times(ykey_value_pair)
        # boolean representing whether the current location is open 
        # according to yesterday's early morning closing time
        within_yesterday: bool = False
        # if this location is not closed all day the day before
        # and that day is open until the next day's morning
        if not (yclosing_hour == yclosing_min == -1) and yclosing_hour > 24:
            yesterday_closing_time: datetime = self.__convert_to_datetime(yclosing_hour, yclosing_min, yesterday)
            within_yesterday = current_time < yesterday_closing_time
        # -------------------------------------------------------------------------
        return (opening_time < current_time < closing_time) or within_yesterday

    def time_till_open(self, location: str, day: str) -> float:
        """
        Figures out the time in minutes until the given location
        will be open on a given day.

        Parameters
        ----------
        location : str
            Name of location as a string.
        day : str
            Name of day as a string.

        Returns
        ----------
        A float representing the time in minutes
        until the given location will be open on the given day.
        If it is closed the entire day or it is already open
        it will return -1.0.
        """
        self.__reset_time()
        key_value_pair: Tuple[str, List[int]] = self.__obtain_hours_key_value(location, day)
        opening_hour, opening_min, *_ = self.__obtain_times(key_value_pair)
        opening_time: datetime = self.__convert_to_datetime(opening_hour, opening_min, day)
        current_time: datetime = self.__convert_to_datetime(self.est.hour, self.est.minute, self.today)
        mins: float = (opening_time - current_time).total_seconds() // 60
        return max(mins, -1.0)

    def time_till_closing(self, location: str, day: str) -> float:
        """
        Figures out the time in minutes until the given location
        will be closed on a given day.

        Parameters
        ----------
        location : str
            Name of location as a string.
        day : str
            Name of day as a string.

        Returns
        ----------
        A float representing the time in minutes
        until the given location will be closed on the given day.
        If it is closed the entire day or it is already closed
        it will return -1.0.
        """
        self.__reset_time()
        key_value_pair: Tuple[str, List[int]] = self.__obtain_hours_key_value(location, day)
        times: List[int] = self.__obtain_times(key_value_pair)
        *_, closing_hour, closing_min = self.__obtain_times(key_value_pair)
        closing_time: td = self.__convert_to_datetime(closing_hour, closing_min, day)
        current_time: td = self.__convert_to_datetime(self.est.hour, self.est.minute, self.today)
        mins: float = (closing_time - current_time).total_seconds() // 60
        return max(mins, -1.0)

    def get_today(self) -> str:
        """
        Gets today's day as an uppercased string.

        Parameters
        ----------
        location : str
            Name of location as a string.

        Returns
        ----------
        A link as a string to the given location.
        """
        self.__reset_time()
        return self.today
    
    def get_link(self, location: str) -> str:
        """
        Gets the link associated with the given location.

        Returns
        ----------
        A string of today's day uppercased.
        Ex: FRIDAY

        Raises
        ----------
        AssertionError: If the given location is not a valid location.
        """
        assert(self.valid_location(location))
        return self.current_location['LINK']

    def closed_all_day(self, location: str, day: str) -> bool:
        """
        Returns a boolean telling whether the given location
        is closed the entire day or not.

        Parameters
        ----------
        location : str
            Name of location as a string.
        day : str
            Name of day as a string.

        Returns
        ----------
        True if the location is closed the entire day, else False.

        Raises
        ----------
        AssertionError: If the given location/day is not a valid location/day.
        """
        assert(self.valid_location(location))
        assert(self.valid_day(day))
        # tuple containing day acronym and time range as a list of 4 integers
        hours_key_value: Tuple[str, List[int]] = self.__obtain_hours_key_value(location, day)
        # if [-1, -1, -1, -1] then it's closed the whole day, else False
        return self.__obtain_times(hours_key_value) == [-1, -1, -1, -1]
