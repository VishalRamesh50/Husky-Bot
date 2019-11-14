import discord
from discord.ext import commands
import NUDining
from datetime import datetime
from pytz import timezone
import string

BOT_SPAM_CHANNEL_ID = 531665740521144341


class Hours(commands.Cog):
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
        self.currDate = datetime(self.year, self.month, self.date)
        self.normal = True  # if normal hours
        # HOLIDAY DATETIME OBJECTS
        self.seniorDtStart = datetime(2019, 4, 27)
        self.seniorDtEnd = datetime(2019, 5, 5)
        self.summer1Start = datetime(2019, 5, 6)
        self.summer1End = datetime(2019, 6, 25)
        self.summer2Start = datetime(2019, 7, 15)
        self.summer2End = datetime(2019, 8, 26)

    # if the message was sent in the BOT_SPAM_CHANNEL or the author is an admin
    def inBotSpam(ctx):
        # if user is a mod
        mod = discord.utils.get(ctx.author.roles, name='Moderator')
        return ctx.channel.id == BOT_SPAM_CHANNEL_ID or mod

    # returns the correct period
    def determinePeriod(self, hour):
        if hour < 12 or hour >= 24:
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
    @commands.check(inBotSpam)
    async def hours(self, ctx, *args):
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
            await ctx.send("Error: Not a valid day.")
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
        elif self.month == 4 and 18 <= self.date <= 26 and self.year == 2019:
            if self.isAlias(self.content, NUDining.FINALS_WEEK_LOCATIONS):
                holiday = " **(Final's Week)**"
                DINING_LOCATIONS = NUDining.FINALS_WEEK_LOCATIONS
                self.normal = False
        elif self.seniorDtStart <= self.currDate <= self.seniorDtEnd:
            if self.isAlias(self.content, NUDining.SENIOR_WEEK_LOCATIONS):
                holiday = " **(Senior Week)**"
                DINING_LOCATIONS = NUDining.SENIOR_WEEK_LOCATIONS
                self.normal = False
        elif self.summer1Start <= self.currDate <= self.summer1End:
            if self.isAlias(self.content, NUDining.SUMMER1_LOCATIONS):
                holiday = " **(Summer 1)**"
                DINING_LOCATIONS = NUDining.SUMMER1_LOCATIONS
                self.normal = False
        elif self.summer2Start <= self.currDate <= self.summer2End:
            if self.isAlias(self.content, NUDining.SUMMER2_LOCATIONS):
                holiday = " **(Summer 2)**"
                DINING_LOCATIONS = NUDining.SUMMER2_LOCATIONS
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
                    if 'MONDAY-THURSDAY' in location:
                        if not (self.day.startswith('S') or self.day.startswith('F')):
                            self.day = 'MONDAY-THURSDAY'
                        if not (yesterday.startswith('S') or yesterday.startswith('F')):
                            yesterday = 'MONDAY-THURSDAY'
                    if 'SATURDAY2' in location:
                        if self.day == 'SATURDAY' and 3 <= self.date <= 9:
                            self.day = 'SATURDAY2'
                        if yesterday == 'SATURDAY' and 3 <= self.date <= 9:
                            yesterday = 'SATURDAY2'
                    if 'SUNDAY2' in location:
                        if self.day == 'SUNDAY' and 4 <= self.date <= 10:
                            self.day = 'SUNDAY2'
                        if yesterday == 'SUNDAY' and 4 <= self.date <= 10:
                            yesterday = 'SUNDAY2'
                if holiday == " **(Patriot's Day)**":
                    if 'TUESDAY-WEDNESDAY' in location:
                        if (self.day.startswith('TU') or self.day.startswith('W')):
                            self.day = 'TUESDAY-WEDNESDAY'
                        if (yesterday.startswith('TU') or yesterday.startswith('W')):
                            yesterday = 'TUESDAY-WEDNESDAY'
                if holiday == " **(Final's Week)**":
                    if 'MONDAY-TUESDAY' in location:
                        if (self.day.startswith('M') or self.day.startswith('TU')):
                            self.day = 'MONDAY-TUESDAY'
                        if (yesterday.startswith('M') or yesterday.startswith('TU')):
                            yesterday = 'MONDAY-TUESDAY'
                    if 'THURSDAY2' in location:
                        if self.day == 'THURSDAY' and 19 <= self.date <= 25:
                            self.day = 'THURSDAY2'
                        if yesterday == 'THURSDAY' and 19 <= self.date <= 25:
                            yesterday = 'THURSDAY2'
                    if 'FRIDAY2' in location:
                        if self.day == 'FRIDAY' and 20 <= self.date <= 26:
                            self.day = 'FRIDAY2'
                        if yesterday == 'FRIDAY' and 20 <= self.date <= 26:
                            yesterday = 'FRIDAY2'
                if holiday == " **(Senior Week)**":
                    if 'MONDAY-WEDNESDAY' in location:
                        if (self.day.startswith('M') or self.day.startswith('TU') or self.day.startswith('W')):
                            self.day = 'MONDAY-WEDNESDAY'
                        if (yesterday.startswith('M') or yesterday.startswith('TU') or yesterday.startswith('W')):
                            yesterday = 'MONDAY-WEDNESDAY'
                    startDt = datetime(2019, 4, 28)
                    if 'SATURDAY & SUNDAY' in location:
                        if self.day == 'SATURDAY' and self.currDate >= startDt:
                            self.day = 'SATURDAY & SUNDAY'
                        if yesterday == 'SATURDAY' and self.currDate >= startDt:
                            yesterday = 'SATURDAY & SUNDAY'
                        startDt = datetime(2019, 4, 29)
                        if self.day == 'SUNDAY' and self.currDate >= startDt:
                            self.day = 'SATURDAY & SUNDAY'
                        if yesterday == 'SUNDAY' and self.currDate >= startDt:
                            yesterday = 'SATURDAY & SUNDAY'
                if holiday == " **(Summer 1)**" or holiday == " **(Summer 2)**":
                    if 'MONDAY-THURSDAY' in location:
                        if not (self.day.startswith('F') or self.day.startswith('S')):
                            self.day = 'MONDAY-THURSDAY'
                        if not (yesterday.startswith('F') or yesterday.startswith('S')):
                            yesterday = 'MONDAY-THURSDAY'
                if 'WEEKDAYS' in location:
                    if not self.day.startswith('S'):
                        self.day = 'WEEKDAYS'
                    if not yesterday.startswith('S'):
                        yesterday = 'WEEKDAYS'
                if 'WEEKENDS' in location:
                    if self.day.startswith('S'):
                        self.day = 'WEEKENDS'
                    if yesterday.startswith('S'):
                        yesterday = 'WEEKENDS'
                if 'EVERYDAY' in location:
                    self.day, yesterday = 'EVERYDAY', 'EVERYDAY'
        # if given location is a valid location
        if self.valid_location:
            link = location['LINK']  # location's link to hours of operation
            # if location is closed for the whole day
            if location[self.day] == "CLOSED":
                self.day = ''.join([i for i in self.day if not i.isdigit()])  # strips day of numbers
                await ctx.send(f"{self.content} is CLOSED {self.day}{holiday}.")
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
                    await ctx.send(hours_of_operation)
                else:
                    # if current time is between opening and closing or between yesterday's closing if it goes into the next day
                    if total_opening <= current_total < total_closing or (yesterday_set and 0 <= current_total <= yesterday_total_closing and yesterday_closing > 24):
                        # if location closes in 60 mins or less
                        if 0 < closing_difference <= 60:
                            await ctx.send(closing_in)
                        # if location closes in 60 mins or less from yesterday's closing time given it closes the next day
                        elif yesterday_set and 0 < yesterday_closing_difference <= 60:
                            await ctx.send(yesterday_closing_in)
                        # if location is open and not closing within 60 mins or less
                        else:
                            await ctx.send(open)
                    # if location is opening within 60 mins
                    elif 0 < opening_difference <= 60:
                        await ctx.send(opening_in)
                    # if location is closed
                    else:
                        await ctx.send(closed)
            # generates link to respective location's hours of operation
            await ctx.send(link)
        # if invalid location was provided
        else:
            # if a comma was not used to separate content and day
            if self.commaError:
                await ctx.send("Error: You must separate the location & day with a comma.")
            # if content is not a valid location
            else:
                await ctx.send(f"Error: Location options are: {NUDining.POSSIBLE_LOCATIONS}")

    # gives a list of all the open locations
    @commands.command()
    @commands.check(inBotSpam)
    async def open(self, ctx):
        self.__init__(self.client)
        self.day = self.EST.strftime("%A").upper()
        LOCATIONS = NUDining.NORMAL_LOCATIONS.copy()  # list of all the dictionaries for each location
        holiday = None
        for key in NUDining.NORMAL_LOCATIONS.keys():
            # FINALS WEEK HOURS
            if self.month == 4 and 18 <= self.date <= 26 and self.year == 2019:
                if key in NUDining.FINALS_WEEK_LOCATIONS:
                    LOCATIONS[key] = NUDining.FINALS_WEEK_LOCATIONS[key]
                    holiday = " (Final's Week)"
            # SENIOR WEEK HOURS
            elif self.seniorDtStart <= self.currDate <= self.seniorDtEnd:
                if key in NUDining.SENIOR_WEEK_LOCATIONS:
                    LOCATIONS[key] = NUDining.SENIOR_WEEK_LOCATIONS[key]
                    holiday = " (Senior Week)"
            # SUMMER 1 HOURS
            elif self.summer1Start <= self.currDate <= self.summer1End:
                if key in NUDining.SUMMER1_LOCATIONS:
                    LOCATIONS[key] = NUDining.SUMMER1_LOCATIONS[key]
                    holiday = " **(Summer 1)**"
            # SUMMER 2 HOURS
            elif self.summer2Start <= self.currDate <= self.summer2End:
                if key in NUDining.SUMMER2_LOCATIONS:
                    LOCATIONS[key] = NUDining.SUMMER2_LOCATIONS[key]
                    holiday = " **(Summer 2)**"
        OPEN_LOCATIONS = []
        for index, dict in enumerate(LOCATIONS.values()):
            day = self.day
            yesterday = self.POSSIBLE_DAYS[(self.POSSIBLE_DAYS.index(self.day) - 1) % len(self.POSSIBLE_DAYS)]  # get yesterday
            if holiday == " (Final's Week)":
                if 'MONDAY-TUESDAY' in dict:
                    if (day.startswith('M') or day.startswith('TU')):
                        day = 'MONDAY-TUESDAY'
                    if (yesterday.startswith('M') or yesterday.startswith('TU')):
                        yesterday = 'MONDAY-TUESDAY'
                if 'THURSDAY2' in dict:
                    if day == 'THURSDAY' and 19 <= self.date <= 25:
                        day = 'THURSDAY2'
                    if yesterday == 'THURSDAY' and 19 <= self.date <= 25:
                        yesterday = 'THURSDAY2'
                if 'FRIDAY' in dict:
                    if day == 'FRIDAY' and 20 <= self.date <= 26:
                        day = 'FRIDAY2'
                    if yesterday == 'FRIDAY' and 20 <= self.date <= 26:
                        yesterday = 'FRIDAY2'
            if holiday == " (Senior Week)":
                if 'MONDAY-WEDNESDAY' in dict:
                    if (day.startswith('M') or day.startswith('TU') or day.startswith('W')):
                        day = 'MONDAY-WEDNESDAY'
                    if (yesterday.startswith('M') or yesterday.startswith('TU') or yesterday.startswith('W')):
                        yesterday = 'MONDAY-WEDNESDAY'
                startDt = datetime(2019, 4, 28)
                if 'SATURDAY & SUNDAY' in dict:
                    if day == 'SATURDAY' and self.currDate >= startDt:
                        day = 'SATURDAY & SUNDAY'
                    if yesterday == 'SATURDAY' and self.currDate >= startDt:
                        yesterday = 'SATURDAY & SUNDAY'
                    startDt = datetime(2019, 4, 29)
                    if day == 'SUNDAY' and self.currDate >= startDt:
                        day = 'SATURDAY & SUNDAY'
                    if yesterday == 'SUNDAY' and self.currDate >= startDt:
                        yesterday = 'SATURDAY & SUNDAY'
            if holiday == " **(Summer 1)**" or holiday == " **(Summer 2)**":
                if 'MONDAY-THURSDAY' in dict:
                    if not (day.startswith('F') or day.startswith('S')):
                        day = 'MONDAY-THURSDAY'
                    if not (yesterday.startswith('F') or yesterday.startswith('S')):
                        yesterday = 'MONDAY-THURSDAY'
            if 'WEEKDAYS' in dict:
                if not day.startswith('S'):
                    day = 'WEEKDAYS'
                if not yesterday.startswith('S'):
                    yesterday = 'WEEKDAYS'
            if 'WEEKENDS' in dict:
                if day.startswith('S'):
                    day = 'WEEKENDS'
                if yesterday.startswith('S'):
                    yesterday = 'WEEKENDS'
            if 'EVERYDAY' in dict:
                day, yesterday = 'EVERYDAY', 'EVERYDAY'
            currentLocation = string.capwords(list(LOCATIONS.keys())[index][0])
            # hours array for current day
            hours = dict[day]
            yesterday_hours = dict[yesterday]
            if hours != 'CLOSED':
                # data from hours array
                opening = hours[0]
                opening_minute = hours[1]
                closing = hours[2]
                closing_minute = hours[3]
                # times converted to 12hr format
                opening_hour = 12 if opening % 12 == 0 else opening % 12   # opening hour in 12hr format
                opening_period = self.determinePeriod(opening)  # AM/PM
                closing_hour = 12 if closing % 12 == 0 else closing % 12   # closing hour in 12hr format
                closing_period = self.determinePeriod(closing)  # AM/PM
                # times in minutes
                openingTime = opening * 60 + int(opening_minute)
                closingTime = closing * 60 + int(closing_minute)
                currentTime = self.hour * 60 + self.minute
                # hours of operation for the current day
                hours_of_operation = f"{opening_hour}:{opening_minute} {opening_period} - {closing_hour}:{closing_minute} {closing_period}"
                # link to the hours of operation for the current location
                link = dict['LINK']

                yesterday_set = False
                try:
                    if yesterday_hours != 'CLOSED':
                        # data from yesterday hours array
                        yesterday_opening = yesterday_hours[0]
                        yesterday_opening_minute = yesterday_hours[1]
                        yesterday_closing = yesterday_hours[2]
                        yesterday_closing_minute = yesterday_hours[3]
                        # times converted to 12hr format
                        yesterday_opening_hour = 12 if yesterday_opening % 12 == 0 else yesterday_opening % 12   # opening hour in 12hr format
                        yesterday_opening_period = self.determinePeriod(yesterday_opening)  # AM/PM
                        yesterday_closing_hour = 12 if yesterday_closing % 12 == 0 else yesterday_closing % 12   # closing hour in 12hr format
                        yesterday_closing_period = self.determinePeriod(yesterday_closing)  # AM/PM
                        # times in minutes
                        yesterday_closingTime = yesterday_closing_hour * 60 + int(yesterday_closing_minute)
                        # hours of operation for the yesterday
                        yesterday_hours_of_operation = f"{yesterday_opening_hour}:{yesterday_opening_minute} {yesterday_opening_period} - {yesterday_closing_hour}:{yesterday_closing_minute} {yesterday_closing_period}"
                        yesterday_set = True
                except KeyError:
                    yesterday_set = False
                # combination of location properties
                combo = {'location': currentLocation, 'link': link}
                # if the current location is open
                if openingTime <= currentTime < closingTime:
                    combo['hours_of_operation'] = hours_of_operation
                    OPEN_LOCATIONS.append(combo)
                elif yesterday_set and 0 <= currentTime < yesterday_closingTime and yesterday_closing > 24:
                    combo['hours_of_operation'] = yesterday_hours_of_operation
                    OPEN_LOCATIONS.append(combo)
        # embedded message sent with all open locations
        embed = discord.Embed(
            description=f"There are {len(OPEN_LOCATIONS)} open locations right now!{holiday if holiday else ''}",
            timestamp=self.EST,
            colour=discord.Colour.green())
        for dict in OPEN_LOCATIONS:
            location = dict['location']
            hours_of_operation = dict['hours_of_operation']
            link = dict['link']
            embed.add_field(name=location, value=f'[{hours_of_operation}]({link})', inline=True)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Hours(client))
