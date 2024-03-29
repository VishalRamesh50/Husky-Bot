import discord
import logging
import os
import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .bot import Bot

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
client = Bot(
    command_prefix=PREFIX,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
    intents=discord.Intents.all(),
)
client.remove_command("help")
