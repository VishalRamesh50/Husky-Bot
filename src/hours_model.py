import nu_dining
from datetime import datetime, timedelta as td
from pytz import timezone
from typing import Tuple, List, Dict, Union


class HoursModel:
    """
    A Model which serves as an intermediary
    for processing Location data providing
    providing methods to compare times.

    Attributes
    ----------
    todays_locations : dict
        a dictionary where keys are a tuple of location name aliases
        and values correspond to LOCATION dictionaries
    current_location : dict
        a dictionary where keys are a sequence of single character day acronyms
        and values correspond to a list of 4 values:
            [opening_hour, opening_min, closing_hour, closing_min]
        or a string indicating a special state. Ex: 'CLOSED
    current_date_range: str
        a string representing the current date_range which the day looking
        for corresponds to in the format: mm/dd/yy-mm/dd/yy
    date_name: str
        the name of the event causing the special hours for the current_date_range
    ORDERED_DAYS: list
        A list of the days of the week in order from Sunday-Saturday all uppercased
    VALID_ACRONYMS: set
        A set of 1 letter uppercased strings corresponding to acronyms of valid days.
    DAYS_TO_ACRONYMS: dict
        A dict where the keys are valid days and the values are the corresponding 1 letter acronyms
    ACRONYMS_TO_DATE: dict
        A dict where the keys are all possible days acronyms and their values are the corresponding valid days.
    est : datetime
        a datetime object representing the current time in the US/Eastern timezone
    today : str
        an uppercased string of Today's Day. Ex: 'FRIDAY'

    Methods
    -------
    valid_location(location_name: str, today_datetime: datetime = None) -> bool
        Determines whether the given location name is a recognized name.
    valid_day(location_name: str) -> bool
        Determines whether the given day is a recognized day.
    location_hours_msg(location: str, day: str) -> str
        Returns a string representing the hours of operation
        for the given location on the given day.
    is_open(location: str, day: str) -> bool
        Determines whether the given location is open on the given day
    time_till_open(location: str, day: str) -> int
        Figures out the time in minutes until the given location
        will be open on a given day.
    time_till_closing(location: str, day: str) -> int
        Figures out the time in minutes until the given location
        will be closed on a given day.
    get_today() -> str
        Gets today's day as an uppercased string.
    get_link(location: str, day: str = None) -> str
        Returns the link associated with the given location on the given day
    closed_all_day(location: str, day: str) -> bool
        Determines whether the given location is closed all day on the given day
    get_available_location() -> str
        Returns a string of all the possible locations in alphabetical order
    """
    def __init__(self):
        # ------------------------------ VARIABLES --------------------------------
        self.todays_locations: Dict[Tuple[str], Dict[str, Union[str, List[int]]]] = nu_dining.NORMAL_LOCATIONS
        self.current_location: Dict[str, Union[str, List[int]]] = None
        self.current_date_range: str = None
        self.date_name: str = ""
        # ------------------------------ CONSTANTS --------------------------------
        self.ORDERED_DAYS: List[str] = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        self.VALID_ACRONYMS: set = {'U', 'M', 'T', 'W', 'R', 'F', 'S'}
        self.DAYS_TO_ACRONYMS: dict = {'SUNDAY': 'U', 'MONDAY': 'M', 'TUESDAY': 'T', 'WEDNESDAY': 'W',
                                       'THURSDAY': 'R', 'FRIDAY': 'F', 'SATURDAY': 'S'}
        self.ACRONYMS_TO_DAYS: dict = dict([(value, key) for key, value in self.DAYS_TO_ACRONYMS.items()])
        self.__ACRONYMS_TO_DAYS2: dict = {'SUN': 'SUNDAY', 'MON': 'MONDAY', 'TU': 'TUESDAY', 'TUE': 'TUESDAY',
        'TUES': 'TUESDAY', 'WED': 'WEDNESDAY', 'TH': 'THURSDAY', 'THU': 'THURSDAY', 'THURS': 'THURSDAY',
        'FRI': 'FRIDAY', 'SAT': 'SATURDAY'}
        self.ACRONYMS_TO_DAYS.update(self.__ACRONYMS_TO_DAYS2)
        # ---------------------------- TIME VARIABLES -----------------------------
        self.est: datetime = datetime.now(timezone('US/Eastern'))
        self.today: str = self.est.strftime("%A").upper()
        # -------------------------------------------------------------------------

    def __reset_time(self):
        self.est: datetime = datetime.now(timezone('US/Eastern'))
        self.today: str = self.est.strftime("%A").upper()

    # TODO: Find a way to keep this from being duplicated since it's common in many classes
    # Possibly create a decorator or make it a function in a Utils class
    def __clean_input(self, input: str) -> str:
        return input.strip().upper()

    def __set_todays_location(self, today_datetime: datetime = None) -> None:
        """
        Sets todays_location, current_date_range, and date_name based on the given datetime.
        Will use today's datetime if None is provided.

        Parameters
        ----------
        today_datetime : `datetime`
            A datetime object to set information relative to.
            Will use current datetime if None is given.
        """
        self.__reset_time()
        # if the date is not given then use the current datetime
        if today_datetime is None:
            today_datetime = self.est
        # create a new datetime object ignoring time and only using date
        today_datetime: datetime = datetime(today_datetime.year, today_datetime.month, today_datetime.day)
        for date_range, location in nu_dining.DATES_TO_LOCATIONS.items():
            start_datetime, end_datetime = self.__get_datetime_range(date_range)
            # if today's date is between a datetime_range for special hours
            if start_datetime <= today_datetime <= end_datetime:
                if start_datetime.year != end_datetime.year:
                    # Ex: " **(DateName: Dec 31-Feb 2,2018)**"
                    self.date_name = f" **({location[0]}: {start_datetime:%b} {start_datetime.day},{start_datetime:%Y}-{end_datetime:%b} {end_datetime.day},{end_datetime:%Y})**"
                elif start_datetime.month != end_datetime.month:
                    # Ex: " **(DateName: Jan 31-Feb 2,2018)**"
                    self.date_name = f" **({location[0]}: {start_datetime:%b} {start_datetime.day}-{end_datetime:%b} {end_datetime.day},{end_datetime:%Y})**"
                else:
                    # Ex: " **(DateName: Jan 1-3,2018)**"
                    self.date_name = f" **({location[0]}: {start_datetime:%b} {start_datetime.day}-{end_datetime.day},{end_datetime:%Y})**"
                self.todays_locations = location[1]
                self.current_date_range = date_range
                return
        # if no special range fit, set default values
        self.todays_locations = nu_dining.NORMAL_LOCATIONS
        self.current_date_range = None
        self.date_name = ""

    def valid_location(self, location_name: str, today_datetime: datetime = None) -> bool:
        """
        Determines whether the given location name is recognized
        as a valid location or an alias of that location from todays_locations
        relative to the given datetime. Will use today's datetime if None is provided.
        Is case-insensitive and ignores whitespace around the location_name.

        Side-effects
        ----------
        Sets the current_location to be the valid location data structure
        if location_name is valid.
        Sets today_location, day_range, and date_name
        according to the given datetime always.

        Parameters
        ----------
        location_name : `str`
            Name of location as a string.
        today_datetime : `datetime`
            A datetime object to set all class variables relative to.

        Returns
        ----------
        True if the given location_name is a valid location else False
        """
        self.__set_todays_location(today_datetime)
        location_name: str = self.__clean_input(location_name)
        for aliases, location in self.todays_locations.items():
            if location_name in aliases:
                self.current_location = location
                return True
        # if the current day range doesn't have certain locations, check if they
        # exist in NORMAL_LOCATIONS
        if self.todays_locations is not nu_dining.NORMAL_LOCATIONS:
            for aliases, location in nu_dining.NORMAL_LOCATIONS.items():
                if location_name in aliases:
                    self.current_location = location
                    # set these variables to indicate that non-holiday data
                    # is being used regardless of the holiday
                    self.todays_locations = nu_dining.NORMAL_LOCATIONS
                    self.current_date_range = None
                    self.date_name = " *(Normal Hours: Not guaranteed to be correct during special hours)*"
                    return True
        # if the name is not found in the current location or NORMAL_LOCATIONS then
        # it is not recognized
        self.current_location = None
        return False

    def valid_day(self, day: str) -> bool:
        """
        Determines whether the given day is a recognized day.
        Is case-insensitive and ignores whitespace around string.

        Parameters
        ----------
        day : `str`
            Name of day as a string.

        Returns
        ----------
        True if the given day is a valid day else False
        """
        day = self.__clean_input(day)
        if day == 'TOMORROW':
            return True
        return day in self.ACRONYMS_TO_DAYS or day in self.ORDERED_DAYS

    def __get_tomorrow(self, day: str) -> str:
        """
        Gets the day after the given day.

        Parameters
        ----------
        day : `str`
            Name of day as a string.

        Returns
        ----------
        A string representing the day after the given day in all caps.

        Raises
        ----------
        `AssertionError`: If the given day is not valid
        """
        # gets the full day and asserts that the day is valid
        day = self.__get_full_day(day)
        curr_index: int = self.ORDERED_DAYS.index(day)
        return self.ORDERED_DAYS[(curr_index + 1) % len(self.ORDERED_DAYS)]

    def __get_full_day(self, day: str) -> str:
        """
        Converts any recognized day acronym to the actual full day name.

        Parameters
        ----------
        day : `str`
            Name of day as a string.

        Returns
        ----------
        A string representing the full day.

        Raises
        ----------
        `AssertionError`: If the given day is not a valid day
        """
        assert(self.valid_day(day))
        day = self.__clean_input(day)
        if day == 'TOMORROW':
            return self.__get_tomorrow(self.get_today())
        return self.ACRONYMS_TO_DAYS.get(day, day)

    def __get_datetime_range(self, date_range: str) -> Tuple[datetime, datetime]:
        """
        Returns a tuple of two datetimes representing the starting and ending date
        given a string in the format mm/dd/yy-mm/dd/yy.

        Parameters
        ----------
        date_range : `str`
            String representing the date range in the format mm/dd/yy-mm/dd/yy.

        Returns
        ----------
        An tuple of size 2 containing the start_datetime and end_datetime
        of the given date_range

        Raises
        ----------
        `AssertionError`: If the given string is not of the valid format: mm/dd/yy-mm/dd/yy
        """
        start_date: str
        end_date: str
        assert '-' in date_range, "Given date range does not have '-'"
        start_date, end_date = date_range.split('-')
        try:
            start_datetime: datetime = datetime.strptime(start_date, '%m/%d/%y')
            end_datetime: datetime = datetime.strptime(end_date, '%m/%d/%y')
            return start_datetime, end_datetime
        except ValueError:
            assert False, 'Given date range is not in the format mm/dd/yy-mm/dd/yy'

    def __get_num_days_in_range(self, day: str, today_datetime: datetime = None) -> int:
        """
        Determines how many of the given day are present between
        the ranges of the current date range.

        Parameters
        ----------
        day : `str`
            Name of day as a string.
        today_datetime : `datetime`
            A datetime object to set todays_location, current_date_range, and date_name to.
            Will use the current datetime if None is given.

        Returns
        ----------
        An `int` representing the number of days between the date range
        of the given day.
        Ex: Monday if range is Jan 1-8, 2019 would return 1,
        Tuesday would return 2
        Will return -1 if there is no special date range set.

        Raises
        ----------
        `AssertionError`: If the given day is not valid.
        """
        self.__set_todays_location(today_datetime)
        # if no there is no special date range set for the given timedate
        if self.current_date_range is None:
            return -1
        # gets the full day and asserts that the day is valid
        day = self.__get_full_day(day)
        # get the start and end datetimes given the date_range
        working_datetime, end_datetime = self.__get_datetime_range(self.current_date_range)
        # while the working datetime is not past the end_range
        while(working_datetime <= end_datetime):
            # if the working datetime's day is the same as the given day
            if working_datetime.strftime('%A').upper() == day:
                return (end_datetime - working_datetime).days // 7 + 1
            working_datetime += td(days=1)
        # if there was no day in the range which had the same day
        return 0

    def __which_day_num(self, day: str, current_datetime: datetime = None) -> int:
        """
        Finds which day number to select when a location has multiple of the same
        day with different times.

        Parameters
        ----------
        day : `str`
            Name of day as a string.
        current_datetime : `datetime`
            The current datetime

        Returns
        ----------
        An int representing which day number past the current day should be used.

        Raises
        ----------
        `AssertionError`: If the given day is not a valid day
        or if the given datetime is not during a special date range.
        """
        # gets the full days and asserts that it's a valid day
        day = self.__get_full_day(day)
        self.__set_todays_location(current_datetime)
        assert self.current_date_range is not None, 'Cannot use this method for non-special date ranges'
        # if a datetime was not given use the current time
        if current_datetime is None:
            current_datetime = self.est
        # get a datetime using just the date and ignoring the time
        current_datetime: datetime = datetime(current_datetime.year, current_datetime.month, current_datetime.day)
        # get the start and end ranges as datetime objects
        working_datetime, end_datetime = self.__get_datetime_range(self.current_date_range)
        # the result to return of which version of the day comes immediately after the current_datetime
        count: int = 0
        while(working_datetime <= end_datetime):
            # if the working datetime's day matches the given day
            if working_datetime.strftime('%A').upper() == day:
                count += 1
                # if the working datetime is past after the current datetime
                if working_datetime >= current_datetime:
                    break
                working_datetime += td(days=7)
            # if there was no day match yet
            else:
                working_datetime += td(days=1)
        return count

    def __obtain_hours_key_value(self, location: str, day: str, today_datetime:datetime = None) -> Tuple[str, List[int]]:
        """
        Searches through the location dictionaries for the current_location
        and then returns the key value pair for the given location which contains
        the range for the given day.

        Parameters
        ----------
        location: `str`
            Name of locations as a string.
        day : `str`
            Name of day as a string.
        today_datetime : `datetime`
            A datetime object get the correct hours-key pair by.

        Returns
        ----------
        Tuple of a String and a List of integers (of length 4)
        Ex: ('MTWR', [11, 0, 20, 0])
        List of integers will be of value -1 if the location is closed the entire day.
        Ex: ('U', [-1, -1, -1, -1])

        Raises
        ----------
        `AssertionError`: If the given location/day is not a valid location/day.
        """
        # gets the full day and asserts that it's a valid day
        day = self.__get_full_day(day)
        self.__reset_time()
        # if no date is given use the current date
        if today_datetime is None:
            today_datetime = self.est
        # move the date to a point where the it's the same day as the given day
        while(today_datetime.strftime('%A').upper() != day):
            today_datetime += td(days=1)
        # confirm that the given location is a valid and sets the current_location
        assert(self.valid_location(location, today_datetime))
        day_acronym: str = self.DAYS_TO_ACRONYMS[day]

        # if there is holiday data being used
        if self.current_date_range is not None:
            num_of_days: int = self.__get_num_days_in_range(day, today_datetime)
            # if there is no day within this range then we must look past this date range
            if num_of_days == 0:
                *_, end_datetime = self.__get_datetime_range(self.current_date_range)
                new_datetime: datetime = end_datetime + td(days=1)
                return self.__obtain_hours_key_value(location, day, new_datetime)
            # if there are more than 1 days in this date range
            elif num_of_days > 1:
                # figure out which day number we should look for
                count:int = self.__which_day_num(day, today_datetime)
                day_acronym += str(count)
        # for each key (which is a string of day acronyms) in the dict of current_location
        for day_aliases, times in self.current_location.items():
            # if the acronym version of the given day is in the string of day_aliases
            if day_acronym in day_aliases:
                # if the location is closed for the entire day
                if times == 'CLOSED':
                    return day_aliases, [-1, -1, -1, -1]
                else:
                    return day_aliases, times

    def __obtain_day_range(self, day_range: str, day: str) -> str:
        """
        Given a key value pair of day range to time as a tuple,
        will return just the day range as a string.

        Parameters
        ----------
        day_range: `str`
            A string which represents a sequence of day acronyms
            corresponding to a range of days.
            Ex: 'MTWR'
        day: `str`
            A string representing a day. This is the day it should find a range
            relative to.
            Ex: 'Friday'

        Returns
        ----------
        May also return "EVERYDAY", "WEEKDAYS", "WEEKENDS".
        If the above are not applicable, will return a string
        representing the starting day to ending day in the format:
        "STARTING_DAY-ENDING_DAY"

        Raises
        ----------
        `AssertionError`: If the day_range does not have at least 1 character
        or if the day is not a valid day.
        """
        # will get the full day and assert that the day is valid
        day = self.__get_full_day(day)
        day_range = self.__clean_input(day_range)
        # remove the digits from the day_range
        day_range = ''.join([i for i in day_range if not i.isdigit()])
        day_acronym: str = self.DAYS_TO_ACRONYMS[day]
        # make sure that the day value has at least 1 character
        assert(len(day_range) > 0)
        # make sure the given day is in the range. Otherwise the range makes not sense.
        assert day_acronym in day_range, 'The given day is not within the given range'
        # if the day range is only one character
        if len(day_range) == 1:
            # convert the single character to a full day name
            return self.ACRONYMS_TO_DAYS[day_range]
        # if the day range is more than one character
        else:
            # if the day range is every single day (at least within this week)
            if set('MTWRFSU').issubset(set(day_range)):
                return 'EVERYDAY'
            # if the day range is all the weekdays and the day searched for is a WEEKDAY
            elif set('MTWRF') == set(day_range) and day_acronym in 'MTWRF':
                return 'WEEKDAYS'
            # if the day range is all the weekends and the day searched for is a WEEKEND
            elif set('SU') == set(day_range) and day_acronym in 'SU':
                return 'WEEKENDS'
            # if the day range is some unique combination of days
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
        hour: `int`
            Number of hours (in 24 time) as an integer.

        Returns
        ----------
        'AM' if the time when fitted into a day is in the morning else 'PM'
        Ex: 25 -> 'AM' or 13 -> 'PM'

        Raises
        ----------
        `AssertionError`: If the given hour is not positive.
        """
        assert hour >= 0, 'Given hour must be positive'
        # convert hour into a 24 hour time
        hour = hour % 24
        # return AM if morning else PM
        return 'AM' if hour < 12 else 'PM'

    def location_hours_msg(self, location: str, day: str) -> str:
        """
        Returns a string stating the hours of operation in a sentence
        for the given location on the given day.

        Parameters
        ----------
        location : `str`
            Name of location as a string.
        day : `str`
            Name of day as a string.

        Returns
        ----------
        String of the format:
        <location> is open from <opening_time> - <closing_time> on <day>
        Ex: STETSON WEST is open from 4:00 PM - 8:00 PM SUNDAY
        or
        <location> is CLOSED <days>
        Ex: STETSON WEST is CLOSED SATURDAY

        Raises
        ----------
        `AssertionError`: If the given location/day is not a valid location/day
        """
        assert(self.valid_location(location))
        location = self.__clean_input(location)
        # gets the full day and asserts that the day is valid
        day = self.__get_full_day(day)
        day_range, times = self.__obtain_hours_key_value(location, day)
        opening_hour, opening_min, closing_hour, closing_min = times
        days = self.__obtain_day_range(day_range, day)
        # if the location has sentinel values with all -1 times, it's closed that entire day
        if opening_hour == opening_min == closing_hour == closing_min == -1:
            return f"{location} is CLOSED {days}{self.date_name}"
        
        hours_of_operation: str = self.get_hours_of_operation(location, day)
        result = (f"{location} is open from "
                  f"{hours_of_operation} "
                  f"{days}{self.date_name}")
        return result
    
    def get_hours_of_operation(self, location: str, day: str) -> str:
        """
        Returns a string representing the hours of operation
        for the given location on the given day.

        Parameters
        ----------
        location : `str`
            Name of location as a string.
        day : `str`
            Name of day as a string.

        Returns
        ----------
        String of the format:
        <opening_time> - <closing_time>
        Ex: "4:00 PM - 8:00 PM"
        or
        "CLOSED"

        Raises
        ----------
        `AssertionError`: If the given location/day is not a valid location/day
        """
        assert(self.valid_location(location))
        location = self.__clean_input(location)
        # gets the full day and asserts that the day is valid
        day = self.__get_full_day(day)
        *_, times = self.__obtain_hours_key_value(location, day)
        opening_hour, opening_min, closing_hour, closing_min = times
        # if the location has sentinel values with all -1 times, it's closed that entire day
        if opening_hour == opening_min == closing_hour == closing_min == -1:
            return 'CLOSED'
        # determine periods for opening and closing (AM/PM)
        opening_period = self.__determine_period(opening_hour)
        closing_period = self.__determine_period(closing_hour)
        # convert opening/closing hours to 12hr time
        opening_hour = opening_hour % 12 or 12
        closing_hour = closing_hour % 12 or 12
        # pad opening/closing mins with 0 if single digit
        opening_min = str(opening_min).zfill(2)
        closing_min = str(closing_min).zfill(2)
        result = (f"{opening_hour}:{opening_min} {opening_period} - "
                  f"{closing_hour}:{closing_min} {closing_period}")
        return result

    def __get_yesterday(self, day: str) -> str:
        """
        Gets the day before the given day.

        Parameters
        ----------
        day : `str`
            Name of day as a string.

        Returns
        ----------
        A string representing the day before the given day in all caps.

        Raises
        ----------
        `AssertionError`: If the given day is not a full day.
        """
        # gets the full day and asserts that it is valid.
        day = self.__get_full_day(day)
        curr_index: int = self.ORDERED_DAYS.index(day)
        return self.ORDERED_DAYS[(curr_index - 1) % len(self.ORDERED_DAYS)]

    def __convert_to_datetime(self, hours: int, mins: int, day: str) -> datetime:
        """
        Creates a datetime object out of the given hours and minutes at the given day
        relative to today's current time and date.

        Parameters
        ----------
        hours : `int`
            time in hours (must be positive)
        mins: `int`
            time in minutes (must be between 0 and 60 [0,60))
        day : `str`
            Name of day as a string

        Returns
        ----------
        True if the location is open else False.

        Raises
        ----------
        `AssertionError`: if hours is negative, mins is not within 0 to 60 [0,60),
        or day is not valid
        """
        assert(hours >= 0)
        assert(0 <= mins < 60)
        # gets the full day and asserts that it is valid
        day = self.__get_full_day(day)
        self.__reset_time()
        diff_of_days, remaining_hours = divmod(hours, 24)

        index_of_curr_day: int = self.ORDERED_DAYS.index(self.today)
        while(True):
            # if yesterday is the given day
            if self.__get_yesterday(self.ORDERED_DAYS[index_of_curr_day]) == day:
                diff_of_days -= 1
                break
            # if a day match is found
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
        location : `str`
            Name of location as a string.
        day : `str`
            Name of day as a string.

        Returns
        ----------
        True if the location is open else False.
        """
        opening_hour, opening_min, closing_hour, closing_min = self.__obtain_hours_key_value(location, day)[1]
        # if it's closed the entire day
        if opening_hour == opening_min == closing_hour == closing_min == -1:
            return False
        opening_time: datetime = self.__convert_to_datetime(opening_hour, opening_min, day)
        closing_time: datetime = self.__convert_to_datetime(closing_hour, closing_min, day)
        current_time: datetime = self.__convert_to_datetime(self.est.hour, self.est.minute, self.today)
        # --------------------------------- YESTERDAY -----------------------------
        yesterday: str = self.__get_yesterday(day)
        *_, yclosing_hour, yclosing_min = self.__obtain_hours_key_value(location, yesterday, current_time + td(days=-1))[1]
        # boolean representing whether the current location is open 
        # according to yesterday's early morning closing time
        within_yesterday: bool = False
        # if this location is not closed all day the day before
        # and that day is open until the next day's morning
        if not (yclosing_hour == yclosing_min == -1) and yclosing_hour > 24:
            yesterday_closing_time: datetime = self.__convert_to_datetime(yclosing_hour, yclosing_min, yesterday)
            within_yesterday = current_time < yesterday_closing_time
        # -------------------------------------------------------------------------
        return (opening_time <= current_time < closing_time) or within_yesterday

    def time_till_open(self, location: str, day: str) -> int:
        """
        Figures out the time in minutes until the given location
        will be open on a given day.

        Parameters
        ----------
        location : `str`
            Name of location as a string.
        day : `str`
            Name of day as a string.

        Returns
        ----------
        An `int` representing the time in minutes
        until the given location will be open on the given day.
        If the given location is closed the entire day will return -1.
        If the given location has already opened it will return 0.
        """
        # if the location is closed the entire day
        if self.closed_all_day(location, day):
            return -1.
        # if the location is currently still open
        if self.is_open(location, day):
            return 0
        opening_hour, opening_min, *_ = self.__obtain_hours_key_value(location, day)[1]
        opening_time: datetime = self.__convert_to_datetime(opening_hour, opening_min, day)
        current_time: datetime = self.__convert_to_datetime(self.est.hour, self.est.minute, self.today)
        mins: int = int((opening_time - current_time).total_seconds() // 60)
        return max(mins, 0)

    def time_till_closing(self, location: str, day: str) -> int:
        """
        Figures out the time in minutes until the given location
        will be closed on a given day.

        Parameters
        ----------
        location : `str`
            Name of location as a string.
        day : `str`
            Name of day as a string.

        Returns
        ----------
        An `int` representing the time in minutes
        until the given location will be closed on the given day.
        If the given location is closed the entire day will return -1.
        If the given location has already closed it will return 0.
        """
        # if the location is closed the entire day
        if self.closed_all_day(location, day):
            return -1
        *_, closing_hour, closing_min = self.__obtain_hours_key_value(location, day)[1]
        closing_time: td = self.__convert_to_datetime(closing_hour, closing_min, day)
        current_time: td = self.__convert_to_datetime(self.est.hour, self.est.minute, self.today)
        # --------------------------------- YESTERDAY -----------------------------
        yesterday: str = self.__get_yesterday(day)
        *_, yclosing_hour, yclosing_min = self.__obtain_hours_key_value(location, yesterday, current_time + td(days=-1))[1]
        # boolean representing whether the current location is open 
        # according to yesterday's early morning closing time
        within_yesterday: bool = False
        # if this location is not closed all day the day before
        # and that day is open until the next day's morning
        if not (yclosing_hour == yclosing_min == -1) and yclosing_hour > 24:
            yesterday_closing_time: datetime = self.__convert_to_datetime(yclosing_hour, yclosing_min, yesterday)
            within_yesterday = current_time < yesterday_closing_time
        # -------------------------------------------------------------------------
        if within_yesterday:
            mins: int = int((yesterday_closing_time - current_time).total_seconds() // 60)
        else:
            mins: int = int((closing_time - current_time).total_seconds() // 60)
        return max(mins, 0)

    def get_today(self) -> str:
        """
        Gets today's day as an uppercased string.

        Returns
        ----------
        A string of today's day uppercased.
        Ex: FRIDAY
        """
        self.__reset_time()
        return self.today
    
    def get_link(self, location: str, day: str = None) -> str:
        """
        Gets the link associated with the given location
        relative to the given day. Will use today's day if
        None is given.

        Parameters
        ----------
        location : `str`
            Name of location as a string.
        day : `str`
            Name of day as a string. Will use today's day if None is given.

        Returns
        ----------
        A string representing the link associated with the given location
        for the given day.

        Raises
        ----------
        `AssertionError`: If the given location/day is not a valid location/day
        """
        self.__reset_time()
        if day is None:
            day = self.get_today()
        # gets the full days and asserts that it is valid
        day = self.__get_full_day(day)
        current_datetime: datetime = datetime(self.est.year, self.est.month, self.est.day)
        # moves the datetime to a place where it's day is the same as the given day
        while(current_datetime.strftime('%A').upper() != day):
            current_datetime += td(days=1)
        assert(self.valid_location(location, current_datetime))
        return self.current_location['LINK']

    def closed_all_day(self, location: str, day: str) -> bool:
        """
        Returns a boolean telling whether the given location
        is closed the entire day or not.

        Parameters
        ----------
        location : `str`
            Name of location as a string.
        day : `str`
            Name of day as a string.

        Returns
        ----------
        True if the location is closed the entire day, else False.

        Raises
        ----------
        `AssertionError`: If the given location/day is not a valid location/day.
        """
        assert(self.valid_location(location))
        # gets the full day and asserts that it is valid
        day = self.__get_full_day(day)
        # tuple containing day acronym and time range as a list of 4 integers
        *_, times = self.__obtain_hours_key_value(location, day)
        # if [-1, -1, -1, -1] then it's closed the whole day, else False
        return times == [-1, -1, -1, -1]
    
    def get_available_locations(self) -> str:
        """
        Return a string representing a comma separated list of all the locations
        that this bot currently serves hours for.
        """
        return nu_dining.POSSIBLE_LOCATIONS
