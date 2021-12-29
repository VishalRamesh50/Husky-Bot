import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
from typing import Optional

from .channel_type import ChannelType


class DBClient:
    def __init__(self, db_connection_url: str) -> None:
        self.db_connection_url: str = db_connection_url
        self.mongo_client = pymongo.MongoClient(self.db_connection_url)

        self.configurator: Database = self.mongo_client.configurator
        self.guild_configs: Collection = self.configurator.guild_configs

        self.hall_of_fame: Database = self.mongo_client.hall_of_fame
        self.hof_sent_messages: Collection = self.hall_of_fame.sent_messages
        self.hof_blacklist: Collection = self.hall_of_fame.blacklist

        self.twitch: Database = self.mongo_client.twitch
        self.twitch_users: Collection = self.twitch.twitch_users
        self.twitch_tracking_data: Collection = self.twitch.twitch_tracking_data

        self.reactions: Database = self.mongo_client.reactions
        self.reactive_channels: Collection = self.reactions.reactive_channels
        self.reactive_roles: Collection = self.reactions.reactive_roles

    def get_guild_configs(self) -> pymongo.CursorType:
        return self.guild_configs.find()

    def configure_channel(
        self, guild_id: int, channel_type: ChannelType, channel_id: int
    ):
        self.configurator.guild_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {channel_type.value: channel_id}},
            upsert=True,
        )

    def message_in_hof(self, guild_id: int, message_id: int) -> bool:
        return bool(
            self.hof_sent_messages.count_documents(
                {"guild_id": guild_id, "messages": message_id}, limit=1
            )
        )

    def add_message_to_hof(self, guild_id: int, message_id: int):
        self.hof_sent_messages.update_one(
            {"guild_id": guild_id}, {"$push": {"messages": message_id}}, upsert=True
        )
        self.hof_sent_messages.create_index("messages")

    def get_hof_blacklist(self) -> pymongo.CursorType:
        return self.hof_blacklist.find()

    def add_to_hof_blacklist(self, guild_id: int, channel_id: int):
        self.hof_blacklist.update_one(
            {"guild_id": guild_id}, {"$push": {"channels": channel_id}}, upsert=True
        )

    def remove_from_hof_blacklist(self, guild_id: int, channel_id: int):
        self.hof_blacklist.update_one(
            {"guild_id": guild_id}, {"$pull": {"channels": channel_id}}
        )

    def get_twitch_users(self) -> pymongo.CursorType:
        return self.twitch_users.find()

    def get_twitch_tracking_data(self) -> pymongo.CursorType:
        return self.twitch_tracking_data.find()

    def add_twitch_user_data(self, user_data):
        self.twitch_users.insert_one(user_data)

    def add_twitch_tracking_data(self, tracking_data):
        self.twitch_tracking_data.insert_one(tracking_data)

    def remove_twitch_tracking_data(self, twitch_login: str, guild_id: int):
        self.twitch_tracking_data.delete_one(
            {"twitch_login": twitch_login, "guild_id": guild_id}
        )

    def remove_twitch_user(self, twitch_login: str):
        self.twitch_users.delete_one({"login": twitch_login})

    def set_twitch_user_offline(self, twitch_login: str):
        self.twitch_tracking_data.update_one(
            {"twitch_login": twitch_login}, {"$set": {"live_message_id": None}}
        )

    def set_twitch_user_live(
        self, twitch_login: str, guild_id: int, live_message_id: int
    ):
        self.twitch_tracking_data.update_one(
            {"twitch_login": twitch_login, "guild_id": guild_id},
            {"$set": {"live_message_id": live_message_id}},
        )

    def find_reaction_channels(self, filter_criteria) -> pymongo.CursorType:
        return self.reactive_channels.find(filter_criteria)

    def find_one_reaction_channel(self, filter_criteria) -> Optional[dict]:
        return self.reactive_channels.find_one(filter_criteria)

    def create_reaction_channel(self, data):
        self.reactive_channels.insert_one(data)

    def reaction_channel_exists(self, filter_criteria) -> bool:
        return bool(self.reactive_channels.count_documents(filter_criteria, limit=1))

    def remove_reaction_channel(self, key: str):
        self.reactive_channels.delete_one({"key": key})

    def find_reaction_roles(self, filter_criteria) -> pymongo.CursorType:
        return self.reactive_roles.find(filter_criteria)

    def find_one_reaction_role(self, filter_criteria) -> Optional[dict]:
        return self.reactive_channels.find_one(filter_criteria)

    def create_reaction_role(self, data):
        self.reactive_roles.insert_one(data)

    def reaction_role_exists(self, filter_criteria) -> bool:
        return bool(self.reactive_roles.count_documents(filter_criteria, limit=1))

    def remove_reaction_role(self, key: str):
        self.reactive_roles.delete_one({"key": key})
