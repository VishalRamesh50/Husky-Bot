import logging
import os
import sentry_sdk
from discord.ext import commands
from dotenv import load_dotenv
from sentry_sdk.integrations.aiohttp import AioHttpIntegration


load_dotenv()
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN and os.environ["ENVIRONMENT"] == "production":
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[AioHttpIntegration()],
    )
logging.basicConfig(level=logging.INFO)


COGS_DIRECTORY = "cogs"
PREFIX = os.environ.get("PREFIX", ".")
client = commands.Bot(command_prefix=PREFIX)
client.remove_command("help")
