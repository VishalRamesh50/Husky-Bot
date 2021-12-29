from enum import Enum


class ChannelType(Enum):
    LOG = "Action Log"
    HOF = "Hall of Fame"
    MODMAIL = "Anonymous Modmail"
    SCHEDULES = "Schedules"
    SUGGESTIONS = "Suggestions"
    TWITCH = "Twitch"
