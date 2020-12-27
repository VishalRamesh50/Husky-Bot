import discord
from discord.ext import commands
from enum import Enum
from typing import Dict, Optional

CHANNEL_TYPE = Enum("ChannelType", "LOG SCHEDULES SUGGESTIONS TWITCH")


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channels: Dict[int, Dict[CHANNEL_TYPE, int]] = {}
        # TODO: call out to the db and cache all the data into this dict first

    def _get_channel(
        self, guild_id: int, channel_type: CHANNEL_TYPE
    ) -> Optional[discord.TextChannel]:
        channel_id: Optional[int] = self.channels.get(guild_id, {}).get(channel_type)
        if channel_id:
            return self.get_channel(channel_id)

    def get_log_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, CHANNEL_TYPE.LOG)

    def get_schedules_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, CHANNEL_TYPE.SCHEDULES)

    def get_suggestions_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, CHANNEL_TYPE.SUGGESTIONS)

    def get_twitch_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        return self._get_channel(guild_id, CHANNEL_TYPE.TWITCH)
