from discord.ext import commands
import NUDining
from datetime import datetime
from pytz import timezone


class Hours:
    def __init__(self, client):
        self.client = client

    # gives the hours of operation for select locations and determines whether open or not
    @commands.command()  # joins voice channel
    async def hours(self, *args):
        POSSIBLE_DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        EST = datetime.now(timezone('US/Eastern'))  # EST timezone
        day = ''
        TODAY = EST.strftime("%A").upper()  # today's day
        hour = int(EST.strftime("%H"))  # current hour 24hr format
        minute = int(EST.strftime("%M"))
        valid_location = False  # whether the given location is valid or not
        month = int(EST.strftime("%m"))
        date = int(EST.strftime("%d"))
        year = int(EST.strftime("%Y"))
        comma = False  # if comma is used in input
        valid_day = False  # if a valid day is present in the input
        commaError = False  # if the comma error should be raised
        content = ''
        #  separates content and optional day from argument by comma
        for word in args:
            if comma:
                day = word.upper()
            elif ',' in word:
                content += word[:-1]
                comma = True
            else:
                content += word + ' '
        content = content.upper()  # makes content uppercase
        parse_location_check = False  # indicates if a recognized location is within the content
        parse_day_check = False  # indicates if a valid day is within the content
        # sets up error checking capability for combinations with an without commas
        if comma:
            if day in POSSIBLE_DAYS + ['TOMORROW']:
                valid_day, parse_day_check = True, True
        else:
            content = content.split()
            for option in POSSIBLE_DAYS + ['TOMORROW']:
                if option in content:
                    parse_day_check = True
                    break
            content = ' '.join(content)
            if not valid_day:
                day = TODAY
                valid_day = True
        original_day = day  # day before changing to location specific key
        # if a valid day is within the content
        if valid_day:
            # if given day is tomorrow
            if day == 'TOMORROW':
                # adds 1 to index getting the next day
                day = POSSIBLE_DAYS[(POSSIBLE_DAYS.index(TODAY) + 1) % len(POSSIBLE_DAYS)]
            # subtracts 1 from index getting the previous day
            yesterday = POSSIBLE_DAYS[(POSSIBLE_DAYS.index(day) - 1) % len(POSSIBLE_DAYS)]  # get yesterday
        else:
            await self.client.say("Error: Not a valid day.")
        # sets the special & holiday string and checks for holidays
        if month == 1 and 18 <= date <= 21 and year == 2019 and day in ['FRIDAY', 'SATURDAY', 'SUNDAY', 'MONDAY']:  # Martin Luther King Weekend
            holiday = "**(Martin Luther King Weekend)**"
            DINING_LOCATIONS = NUDining.MLK_LOCATIONS
        elif month == 2 and 15 <= date <= 18 and year == 2019 and day in ['FRIDAY', 'SATURDAY', 'SUNDAY', 'MONDAY']:  # Presidents' Day Weekend
            holiday = "**(Presidents' Day Weekend)**"
            DINING_LOCATIONS = NUDining.PRESIDENTS_LOCATIONS
        elif month == 3 and 1 <= date <= 10:
            holiday = "**(Spring Break)**"
            DINING_LOCATIONS = NUDining.SPRING_BREAK_LOCATIONS
        else:
            holiday = ''
            DINING_LOCATIONS = NUDining.NORMAL_LOCATIONS
        # check if given content is a valid location
        for possibilities in DINING_LOCATIONS.keys():
            if content in possibilities:
                valid_location, parse_location_check = True, True
                break
            # check if a location alias is in the content
            for options in possibilities:
                if options in content:
                    parse_location_check = True
        # check for comma error
        if (parse_location_check or (parse_day_check and not valid_location)) and not comma:
            commaError = True
        # Sets location, content name, and unique day keys if relevant
        for aliases in DINING_LOCATIONS:
            if content in aliases:
                content = aliases[0]  # sets content to full location name
                location = DINING_LOCATIONS[aliases]  # sets location to corresponding dictionary
                # Set given day to location specific keys if necessary
                if holiday == "**(Spring Break)**":
                    if 'MONDAY-THURSDAY' in location.keys():
                        if not (day.startswith('S') or day.startswith('F')):
                            day = 'MONDAY-THURSDAY'
                        if not (yesterday.startswith('S') or yesterday.startswith('F')):
                            yesterday = 'MONDAY-THURSDAY'
                    if 'SATURDAY2' in location.keys():
                        if day == 'SATURDAY' and 3 <= date <= 9:
                            day = 'SATURDAY2'
                        if yesterday == 'SATURDAY' and 3 <= date <= 9:
                            yesterday = 'SATURDAY2'
                    if 'SUNDAY2' in location.keys():
                        if day == 'SUNDAY' and 4 <= date <= 10:
                            day = 'SUNDAY2'
                        if yesterday == 'SUNDAY' and 4 <= date <= 10:
                            yesterday = 'SUNDAY2'
                if 'WEEKDAYS' in location.keys():
                    if not day.startswith('S'):
                        day = 'WEEKDAYS'
                    if not yesterday.startswith('S'):
                        yesterday = 'WEEKDAYS'
                if 'WEEKENDS' in location.keys():
                    if day.startswith('S'):
                        day = 'WEEKENDS'
                    if yesterday.startswith('S'):
                        yesterday = 'WEEKENDS'
                if 'EVERYDAY' in location.keys():
                    day, yesterday = 'EVERYDAY', 'EVERYDAY'
        # if given location is a valid location
        if valid_location:
            link = location['LINK']  # location's link to hours of operation
            # if location is closed for the whole day
            if location[day] == "CLOSED":
                await self.client.say(f"{content} is CLOSED {''.join([i for i in day if not i.isdigit()])} {holiday}.")
            else:
                current_total = hour * 60 + minute  # current time converted to minutes
                # TODAY HOURS VARIABLES
                opening = location[day][0]  # opening hour in 24hr format
                opening_hour = opening % 12  # opening hour in 12hr format
                # since 12%12=0, convert to 12
                if opening_hour == 0:
                    opening_hour = 12
                opening_minute = location[day][1]
                opening_period = NUDining.determinePeriod(opening)  # AM/PM
                closing = location[day][2]  # closing hour in 24hr format
                closing_hour = closing % 12  # closing hour in 12hr format
                # since 12%12=0, convert to 12
                if closing_hour == 0:
                    closing_hour = 12
                closing_minute = location[day][3]
                closing_period = NUDining.determinePeriod(closing)  # AM/PM
                day = ''.join([i for i in day if not i.isdigit()])  # strips the day of any numbers in case it is a 2nd version day from a holiday
                hours_of_operation = f"{content} is open from {opening_hour}:{opening_minute} {opening_period} - {closing_hour}:{closing_minute} {closing_period} {day} {holiday}."
                open = f"{content} is OPEN now! {hours_of_operation}"
                closed = f"{content} is CLOSED now. {hours_of_operation}"
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
                        yesterday_closing_period = NUDining.determinePeriod(yesterday_closing)  # AM/PM
                        yesterday_hours_of_operation = f"{content} is open till {yesterday_closing_hour}:{yesterday_closing_min} {yesterday_closing_period} and {hours_of_operation}"
                        yesterday_open = f"{content} is OPEN now! {yesterday_hours_of_operation}"
                        yesterday_total_closing = yesterday_closing_hour * 60 + int(closing_minute)
                        yesterday_closing_difference = yesterday_total_closing - (hour * 60 + minute)
                        yesterday_closing_in = f"{yesterday_open} It will be closing in {yesterday_closing_difference} minutes!"
                        yesterday_set = True  # determines if yesterday's variables were set
                # if yesterday is not within a location (Ex: for holidays)
                except KeyError:
                    yesterday_set = False
                # if a day was specified
                if original_day != TODAY:
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
            if commaError:
                await self.client.say("Error: You must separate the location & day with a comma.")
            # if content is not a valid location
            else:
                await self.client.say(f"Error: Location options are: {NUDining.POSSIBLE_LOCATIONS}")


def setup(client):
    client.add_cog(Hours(client))
