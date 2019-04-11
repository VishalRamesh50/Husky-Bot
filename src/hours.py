from discord.ext import commands
import NUDining
from datetime import datetime
from pytz import timezone


class Hours:
    def __init__(self, client):
        self.client = client
        self.POSSIBLE_DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        self.day = ''
        self.comma = False  # if comma is used in input
        self.valid_day = False  # if a valid day is present in the input
        self.valid_location = False  # whether the given location is valid or not
        self.commaError = False  # if the comma error should be raised
        self.content = ''
        self.parse_location_check = False  # indicates if a recognized location is within the content
        self.parse_day_check = False  # indicates if a valid day is within the content
        self.EST = datetime.now(timezone('US/Eastern'))  # EST timezone
        self.TODAY = self.EST.strftime("%A").upper()  # today's day
        self.hour = int(self.EST.strftime("%H"))  # current hour 24hr format
        self.minute = int(self.EST.strftime("%M"))
        self.month = int(self.EST.strftime("%m"))
        self.date = int(self.EST.strftime("%d"))
        self.year = int(self.EST.strftime("%Y"))
        self.normal = True  # if normal hours

    # returns the correct period
    def determinePeriod(self, hour):
        if hour < 12 or hour > 24:
            return 'AM'
        else:
            return 'PM'

    # determines if a given location is one of the aliases in the given Dictionary
    def isAlias(self, location, dictionary):
        for possibilities in dictionary.keys():
            if location in possibilities:
                return True
        return False

    # separates location and day by comma
    def parseComma(self, args):
        args = ' '.join(args).split(',')
        try:
            self.day = args[1].upper().strip()
            self.comma = True
        except IndexError:
            pass
        self.content = args[0].upper().strip()

    # gives the hours of operation for select locations and determines whether open or not
    @commands.command()
    async def hours(self, *args):
        self.__init__(self.client)  # re-initialize variables
        #  separates content and optional day from argument by comma
        self.parseComma(args)
        # sets up error checking capability for combinations with an without commas
        self.parse_day_check = self.day in self.POSSIBLE_DAYS + ['TOMORROW']
        if self.comma:
            self.valid_day = self.day in self.POSSIBLE_DAYS + ['TOMORROW']
        else:
            if not self.valid_day:
                self.day = self.TODAY
                self.valid_day = True
        original_day = self.day  # day before changing to location specific key
        # if a valid day is within the content
        if self.valid_day:
            # if given day is tomorrow
            if self.day == 'TOMORROW':
                # adds 1 to index getting the next day
                self.day = self.POSSIBLE_DAYS[(self.POSSIBLE_DAYS.index(self.TODAY) + 1) % len(self.POSSIBLE_DAYS)]
            # subtracts 1 from index getting the previous day
            yesterday = self.POSSIBLE_DAYS[(self.POSSIBLE_DAYS.index(self.day) - 1) % len(self.POSSIBLE_DAYS)]  # get yesterday
        else:
            await self.client.say("Error: Not a valid day.")
        # sets the special & holiday string and checks for holidays
        if self.month == 1 and 18 <= self.date <= 21 and self.year == 2019 and self.day in ['FRIDAY', 'SATURDAY', 'SUNDAY', 'MONDAY']:  # Martin Luther King Weekend
            if self.isAlias(self.content, NUDining.MLK_LOCATIONS):
                holiday = " **(Martin Luther King Weekend)**"
                DINING_LOCATIONS = NUDining.MLK_LOCATIONS
                self.normal = False
        elif self.month == 2 and 15 <= self.date <= 18 and self.year == 2019 and self.day in ['FRIDAY', 'SATURDAY', 'SUNDAY', 'MONDAY']:  # Presidents' Day Weekend
            if self.isAlias(self.content, NUDining.PRESIDENTS_LOCATIONS):
                holiday = " **(Presidents' Day Weekend)**"
                DINING_LOCATIONS = NUDining.PRESIDENTS_LOCATIONS
                self.normal = False
        elif self.month == 3 and 1 <= self.date <= 10 and self.year == 2019:
            if self.isAlias(self.content, NUDining.SPRING_BREAK_LOCATIONS):
                holiday = " **(Spring Break)**"
                DINING_LOCATIONS = NUDining.SPRING_BREAK_LOCATIONS
                self.normal = False
        elif self.month == 4 and 11 <= self.date <= 17 and self.year == 2019:
            if self.isAlias(self.content, NUDining.PATRIOTS_DAY_LOCATIONS):
                holiday = " **(Patriot's Day)**"
                DINING_LOCATIONS = NUDining.PATRIOTS_DAY_LOCATIONS
                self.normal = False
        if self.normal:
            holiday = ''
            DINING_LOCATIONS = NUDining.NORMAL_LOCATIONS
        # check if given content is a valid location
        for possibilities in DINING_LOCATIONS.keys():
            if self.content in possibilities:
                self.valid_location, self.parse_location_check = True, True
                break
            # check if a location alias is in the content
            for options in possibilities:
                if options in self.content:
                    self.parse_location_check = True
        # check for comma error
        if (self.parse_location_check or (self.parse_day_check and not self.valid_location)) and not self.comma:
            self.commaError = True
        # Sets location, content name, and unique day keys if relevant
        for aliases in DINING_LOCATIONS:
            if self.content in aliases:
                self.content = aliases[0]  # sets content to full location name
                location = DINING_LOCATIONS[aliases]  # sets location to corresponding dictionary
                # Set given day to location specific keys if necessary
                if holiday == " **(Spring Break)**":
                    if 'MONDAY-THURSDAY' in location.keys():
                        if not (self.day.startswith('S') or self.day.startswith('F')):
                            self.day = 'MONDAY-THURSDAY'
                        if not (yesterday.startswith('S') or yesterday.startswith('F')):
                            yesterday = 'MONDAY-THURSDAY'
                    if 'SATURDAY2' in location.keys():
                        if self.day == 'SATURDAY' and 3 <= self.date <= 9:
                            self.day = 'SATURDAY2'
                        if yesterday == 'SATURDAY' and 3 <= self.date <= 9:
                            yesterday = 'SATURDAY2'
                    if 'SUNDAY2' in location.keys():
                        if self.day == 'SUNDAY' and 4 <= self.date <= 10:
                            self.day = 'SUNDAY2'
                        if yesterday == 'SUNDAY' and 4 <= self.date <= 10:
                            yesterday = 'SUNDAY2'
                if holiday == " **(Patriot's Day)**":
                    if 'TUESDAY-WEDNESDAY' in location.keys():
                        if (self.day.startswith('TU') or self.day.startswith('W')):
                            self.day = 'TUESDAY-WEDNESDAY'
                        if (yesterday.startswith('TU') or yesterday.startswith('W')):
                            yesterday = 'TUESDAY-WEDNESDAY'
                if 'WEEKDAYS' in location.keys():
                    if not self.day.startswith('S'):
                        self.day = 'WEEKDAYS'
                    if not yesterday.startswith('S'):
                        yesterday = 'WEEKDAYS'
                if 'WEEKENDS' in location.keys():
                    if self.day.startswith('S'):
                        self.day = 'WEEKENDS'
                    if yesterday.startswith('S'):
                        yesterday = 'WEEKENDS'
                if 'EVERYDAY' in location.keys():
                    self.day, yesterday = 'EVERYDAY', 'EVERYDAY'
        # if given location is a valid location
        if self.valid_location:
            link = location['LINK']  # location's link to hours of operation
            # if location is closed for the whole day
            if location[self.day] == "CLOSED":
                self.day = ''.join([i for i in self.day if not i.isdigit()])  # strips day of numbers
                await self.client.say(f"{self.content} is CLOSED {self.day}{holiday}.")
            else:
                current_total = self.hour * 60 + self.minute  # current time converted to minutes
                # TODAY HOURS VARIABLES
                opening = location[self.day][0]  # opening hour in 24hr format
                opening_hour = opening % 12  # opening hour in 12hr format
                # since 12%12=0, convert to 12
                if opening_hour == 0:
                    opening_hour = 12
                opening_minute = location[self.day][1]
                opening_period = self.determinePeriod(opening)  # AM/PM
                closing = location[self.day][2]  # closing hour in 24hr format
                closing_hour = closing % 12  # closing hour in 12hr format
                # since 12%12=0, convert to 12
                if closing_hour == 0:
                    closing_hour = 12
                closing_minute = location[self.day][3]
                closing_period = self.determinePeriod(closing)  # AM/PM
                self.day = ''.join([i for i in self.day if not i.isdigit()])  # strips the day of any numbers in case it is a 2nd version day from a holiday
                hours_of_operation = f"{self.content} is open from {opening_hour}:{opening_minute} {opening_period} - {closing_hour}:{closing_minute} {closing_period} {self.day}{holiday}."
                open = f"{self.content} is OPEN now! {hours_of_operation}"
                closed = f"{self.content} is CLOSED now. {hours_of_operation}"
                total_opening = opening * 60 + int(opening_minute)
                total_closing = closing * 60 + int(closing_minute)
                opening_difference = total_opening - current_total
                closing_difference = total_closing - current_total
                closing_in = f"{open} It will be closing in {closing_difference} minutes!"
                opening_in = f"{closed} It will be opening in {opening_difference} minutes!"
                # YESTERDAY HOURS VARIABLES
                yesterday_set = False  # yesterday's closing_hour 24hr format
                try:
                    if location[yesterday] != "CLOSED":
                        yesterday_closing = location[yesterday][2]  # yesterday's closing_hour 24hr format
                        # if yesterday doesn't close in the next day then set to the same as today's closing
                        if yesterday_closing <= 24:
                            yesterday_closing = closing
                        yesterday_closing_hour = yesterday_closing % 12
                        # since 12%12=0, convert to 12
                        if yesterday_closing_hour == 0:
                            yesterday_closing_hour = 12
                        yesterday_closing_min = location[yesterday][3]  # yesterday's closing minute
                        yesterday_closing_period = self.determinePeriod(yesterday_closing)  # AM/PM
                        yesterday_hours_of_operation = f"{self.content} is open till {yesterday_closing_hour}:{yesterday_closing_min} {yesterday_closing_period} and {hours_of_operation}"
                        yesterday_open = f"{self.content} is OPEN now! {yesterday_hours_of_operation}"
                        yesterday_total_closing = yesterday_closing_hour * 60 + int(closing_minute)
                        yesterday_closing_difference = yesterday_total_closing - (self.hour * 60 + self.minute)
                        yesterday_closing_in = f"{yesterday_open} It will be closing in {yesterday_closing_difference} minutes!"
                        yesterday_set = True  # determines if yesterday's variables were set
                # if yesterday is not within a location (Ex: for holidays)
                except KeyError:
                    yesterday_set = False
                # if a day was specified
                if original_day != self.TODAY:
                    await self.client.say(hours_of_operation)
                else:
                    # if current time is between opening and closing or between yesterday's closing if it goes into the next day
                    if total_opening <= current_total < total_closing or (yesterday_set and 0 <= current_total <= yesterday_total_closing and yesterday_closing > 24):
                        # if location closes in 60 mins or less
                        if 0 < closing_difference <= 60:
                            await self.client.say(closing_in)
                        # if location closes in 60 mins or less from yesterday's closing time given it closes the next day
                        elif yesterday_set and 0 < yesterday_closing_difference <= 60:
                            await self.client.say(yesterday_closing_in)
                        # if location is open and not closing within 60 mins or less
                        else:
                            await self.client.say(open)
                    # if location is opening within 60 mins
                    elif 0 < opening_difference <= 60:
                        await self.client.say(opening_in)
                    # if location is closed
                    else:
                        await self.client.say(closed)
            # generates link to respective location's hours of operation
            await self.client.say(link)
        # if invalid location was provided
        else:
            # if a comma was not used to separate content and day
            if self.commaError:
                await self.client.say("Error: You must separate the location & day with a comma.")
            # if content is not a valid location
            else:
                await self.client.say(f"Error: Location options are: {NUDining.POSSIBLE_LOCATIONS}")


def setup(client):
    client.add_cog(Hours(client))
