import discord
import os
import pymongo
from collections import defaultdict
from discord.ext import commands
from enum import Enum
from pymongo.collection import Collection
from typing import Dict, Optional


class ChannelType(Enum):
    LOG = "Action Log"
    MODMAIL = "Anonymous Modmail"
    SCHEDULES = "Schedules"
    SUGGESTIONS = "Suggestions"
    TWITCH = "Twitch"


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel_config: Dict[int, Dict[ChannelType, int]] = defaultdict(dict)
        DB_CONNECTION_URL = os.environ["DB_CONNECTION_URL"]
        mongoClient = pymongo.MongoClient(DB_CONNECTION_URL)
        guild_configs: Collection = mongoClient.configurator.guild_configs
        for document in guild_configs.find():
            guild_id: int = document["guild_id"]
            del document["_id"]
            del document["guild_id"]
            self.channel_config[guild_id] = document

    def _get_channel(
        self, guild_id: int, channel_type: ChannelType
    ) -> Optional[discord.TextChannel]:
        channel_id: Optional[int] = self.channel_config[guild_id].get(channel_type)
        if channel_id:
            return self.get_channel(channel_id)

    def get_log_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.LOG)

    def get_schedules_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.SCHEDULES)

    def get_suggestions_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.SUGGESTIONS)

    def get_twitch_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.TWITCH)
