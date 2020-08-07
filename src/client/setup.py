import discord
import logging
import os
import sentry_sdk
from discord.ext import commands
from dotenv import load_dotenv
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from data.ids import ADMIN_ROLE_ID, MODERATOR_ROLE_ID

load_dotenv()
SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ["ENVIRONMENT"]
if SENTRY_DSN and ENVIRONMENT == "production":
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=None)
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        integrations=[sentry_logging, AioHttpIntegration()],
    )
logging.basicConfig(level=logging.INFO)


COGS_DIRECTORY = "cogs"
PREFIX = os.environ.get("PREFIX", ".")
client = commands.Bot(
    command_prefix=PREFIX,
    allowed_mentions=discord.AllowedMentions(
        everyone=False,
        roles=[discord.Object(ADMIN_ROLE_ID), discord.Object(MODERATOR_ROLE_ID)],
    ),
)
client.remove_command("help")
