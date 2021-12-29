import discord
import os
from collections import defaultdict
from discord.ext import commands
from enum import Enum
from typing import Dict, Optional, Union

from .db import DBClient


class ChannelType(Enum):
    LOG = "Action Log"
    HOF = "Hall of Fame"
    MODMAIL = "Anonymous Modmail"
    SCHEDULES = "Schedules"
    SUGGESTIONS = "Suggestions"
    TWITCH = "Twitch"


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel_config: Dict[int, Dict[str, int]] = defaultdict(dict)
        self.db = DBClient(os.environ["DB_CONNECTION_URL"])
        for document in self.db.get_guild_configs():
            guild_id: int = document["guild_id"]
            del document["_id"]
            del document["guild_id"]
            self.channel_config[guild_id] = document

    def _get_channel(
        self, guild_id: int, channel_type: ChannelType
    ) -> Optional[Union[discord.abc.GuildChannel, discord.abc.PrivateChannel]]:
        channel_id: Optional[int] = self.channel_config[guild_id].get(
            channel_type.value
        )
        if channel_id:
            return self.get_channel(channel_id)

    def get_log_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.LOG)

    def get_hof_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.HOF)

    def get_modmail_channel(self, guild_id: int) -> Optional[discord.CategoryChannel]:
        return self._get_channel(guild_id, ChannelType.MODMAIL)

    def get_schedules_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.SCHEDULES)

    def get_suggestions_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.SUGGESTIONS)

    def get_twitch_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, ChannelType.TWITCH)
