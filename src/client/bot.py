import discord
from discord.ext import commands
from enum import Enum
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
        self.channels: Dict[int, Dict[ChannelType, int]] = {}
        # TODO: call out to the db and cache all the data into this dict first

    def _get_channel(
        self, guild_id: int, channel_type: ChannelType
    ) -> Optional[discord.TextChannel]:
        channel_id: Optional[int] = self.channels.get(guild_id, {}).get(channel_type)
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
