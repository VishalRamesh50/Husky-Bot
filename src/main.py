import logging
import os

from client.setup import client, COGS_DIRECTORY
from client import misc, error_handlers

logger = logging.getLogger(__name__)

EXTENSIONS = [
    "activity",
    "anonymous_modmail",
    "aoun",
    "clear",
    "course_registration",
    "day",
    "hall_of_fame",
    "help",
    "icecream",
    "it_be_like_that",
    "loader",
    "logs",
    "misc",
    "onboarding",
    "reaction",
    "reminder",
    "schedules",
    "stats",
    "twitch",
]


if __name__ == "__main__":
    # loads all extensions
    for extension in EXTENSIONS:
        try:
            client.load_extension(f"{COGS_DIRECTORY}.{extension}")
        except Exception as error:
            logger.warning(f"{extension} cannot be loaded. [{error}]")
    # create event to cycle through presences
    misc.change_status.start()
    # start bot
    client.run(os.environ["TOKEN"])
