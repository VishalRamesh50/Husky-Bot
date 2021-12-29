import asyncio
import discord
import logging
import os
import requests
from collections import defaultdict
from datetime import datetime
from discord.ext import commands, tasks
from typing import Dict, Optional, Set

from client.bot import Bot, ChannelType
from checks import is_admin
from utils import required_configs

TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
TWITCH_CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"]

logger = logging.getLogger(__name__)


class Twitch(commands.Cog):
    """
    Manages Twitch related integrations.

    Attributes
    ----------
    client : `commands.Bot`
        a client connection to Discord to interact with the Discord WebSocket and APIs
    TWITCH_CHECK_TIME : `int`
        This module will check for live streams every TWITCH_CHECK_TIME number of seconds

    Methods
    -------
    addTwitch(ctx: commands.Context, twitch_user: str, member: discord.Member)
        Adds a Twitch user to be tracked.
    removeTwitch(ctx: commands.Context, twitch_user: str)
        Removes a Twitch user from being tracked.
    listTwitch(ctx: commands.Context)
        List the current Twitch users being tracked.

    """

    def __init__(self, client: Bot):
        self.client = client
        self.TWITCH_CHECK_TIME = 30
        self.__set_auth_token()
        self.twitch_login_user_data: Dict[str, Dict] = {}
        self.guild_to_tracked_logins: Dict[int, Set[str]] = defaultdict(set)
        # twitch login to guild_id to tracking data
        self.twitch_tracking_data: Dict[
            str, Dict[int, Dict[str, Optional[int]]]
        ] = defaultdict(dict)
        for twitch_user_data in self.client.db.get_twitch_users():
            login: str = twitch_user_data["login"]
            self.twitch_login_user_data[login] = twitch_user_data
        for twitch_tracking_data in self.client.db.get_twitch_tracking_data():
            login = twitch_tracking_data["login"]
            guild_id: int = twitch_tracking_data["guild_id"]
            self.guild_to_tracked_logins[guild_id].add(login)
            member_id: Optional[int] = twitch_tracking_data["member_id"]
            live_message_id: Optional[int] = twitch_tracking_data["live_message_id"]
            self.twitch_tracking_data[login][guild_id] = {
                "member_id": member_id,
                "live_message_id": live_message_id,
            }
        self.check_twitch.start()  # iniate loop for twitch notifs

    def cog_unload(self):
        """Cancel loop for looking at live streams when Twitch module is unloaded."""
        self.check_twitch.cancel()

    def __set_auth_token(self) -> None:
        """
        Returns the Twitch API response for requesting an OAuth token which
        is required for Twitch API requests as of May 1st, 2020.

        Returns
        ----------
        The access_token from a response in the format:
        {
            "access_token": "<user access token>",
            "expires_in": <number of seconds until the token expires>,
            "token_type": "bearer"
        }
        """
        response: requests.Response = requests.post(
            f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}"
            f"&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials"
        )
        self.TWITCH_AUTH_TOKEN = response.json()["access_token"]

    def __get_user_response(self, login: str) -> requests.Response:
        """
        Returns the Twitch API response for a user given a login

        Parameters
        ----------
        login : `str`
            The login name of the Twitch user

        Returns
        ----------
        A response containing the format:
        {
            "data": [
                {
                    "id": int,
                    "login": str,
                    "display_name": str,
                    "type": str,
                    "broadcaster_type": str,
                    "description": str,
                    "profile_image_url": str,
                    "offline_image_url": str,
                    "view_count": int
                }
            ]
        }
        """
        response: requests.Response = requests.get(
            f"https://api.twitch.tv/helix/users?login={login}",
            headers={
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {self.TWITCH_AUTH_TOKEN}",
            },
        )
        if response.status_code == 401:
            self.__set_auth_token()
            response = requests.get(
                f"https://api.twitch.tv/helix/users?login={login}",
                headers={
                    "Client-ID": TWITCH_CLIENT_ID,
                    "Authorization": f"Bearer {self.TWITCH_AUTH_TOKEN}",
                },
            )
        return response

    def __get_stream_response(self, login: str) -> requests.Response:
        """
        Returns the Twitch API response for a live stream given a login

        Parameters
        ----------
        login : `str`
            The login name of the Twitch user

        Returns
        ----------
        A response containing the format:
        {
            "data": [
                {
                    "id": int,
                    "user_id": int,
                    "user_name": str,
                    "game_id": int,
                    "type": str,
                    "title": str,
                    "viewer_count": int,
                    "started_at": datetime,
                    "language": str,
                    "thumbnail_url": str,
                    "tag_ids": [str]
                }
            ],
            "pagination": {
                "cursor": str
            }
        }
        """
        response: requests.Response = requests.get(
            f"https://api.twitch.tv/helix/streams?user_login={login}",
            headers={
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {self.TWITCH_AUTH_TOKEN}",
            },
        )
        if response.status_code == 401:
            self.__set_auth_token()
            response = requests.get(
                f"https://api.twitch.tv/helix/streams?user_login={login}",
                headers={
                    "Client-ID": TWITCH_CLIENT_ID,
                    "Authorization": f"Bearer {self.TWITCH_AUTH_TOKEN}",
                },
            )
        return response

    def __get_game_response(self, game_id: str) -> requests.Response:
        """
        Returns the Twitch API response for a game given a login

        Parameters
        ----------
        game_id : `str`
            The associated twitch_id for the game.

        Returns
        ----------
        A response containing the format:
        {
            "data": [
                {
                    "id": int,
                    "name": str,
                    "box_art_url": str
                }
            ]
        }
        """
        response: requests.Response = requests.get(
            f"https://api.twitch.tv/helix/games?id={game_id}",
            headers={
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {self.TWITCH_AUTH_TOKEN}",
            },
        )
        if response.status_code == 401:
            response = requests.get(
                f"https://api.twitch.tv/helix/games?id={game_id}",
                headers={
                    "Client-ID": TWITCH_CLIENT_ID,
                    "Authorization": f"Bearer {self.TWITCH_AUTH_TOKEN}",
                },
            )
        return response

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["addTwitch"])
    @required_configs(ChannelType.TWITCH)
    async def add_twitch(
        self, ctx: commands.Context, twitch_user: str, member: discord.Member = None
    ) -> None:
        """
        Adds a twitch user to track and send notifications for when they go live.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        twitch_user : `str`
            The twitch_username to track.
        """

        guild_id: int = ctx.guild.id
        user_response: requests.Response = self.__get_user_response(twitch_user)
        if user_response.status_code != 200:
            await ctx.send("Failed to retreive user data. Try again.")
            logger.warning(user_response.json())
            return

        user_response_data: list = user_response.json()["data"]
        if not user_response_data:
            await ctx.send(f"No Twitch user `{twitch_user}` found.")
            return

        member_id: Optional[int] = member.id if member else None
        user_data: dict = user_response_data[0]
        user_id: str = user_data["id"]
        login: str = user_data["login"]
        display_name: str = user_data["display_name"]
        description: str = user_data["description"]
        profile_url: str = user_data["profile_image_url"]
        view_count: int = user_data["view_count"]

        if login not in self.twitch_login_user_data:
            self.client.db.add_twitch_user_data(user_data)
            self.twitch_login_user_data[login] = user_data
        if login not in self.guild_to_tracked_logins[guild_id]:
            member_and_live_message_data = {
                "member_id": member_id,
                "live_message_id": None,
            }
            self.client.db.add_twitch_tracking_data(
                {
                    "twitch_login": login,
                    "guild_id": ctx.guild.id,
                    **member_and_live_message_data,
                }
            )
            self.guild_to_tracked_logins[guild_id].add(login)
            self.twitch_tracking_data[login][guild_id] = member_and_live_message_data
            await ctx.send(f"Started to track Twitch user `{display_name}`.")
            embed = discord.Embed(
                description=description, color=discord.Color.dark_purple()
            )
            embed.set_author(name=display_name, icon_url=profile_url)
            embed.set_thumbnail(url=profile_url)
            embed.add_field(name="Total Viewers", value=view_count, inline=True)
            embed.set_footer(text=f"User ID: {user_id}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                f"The Twitch user `{display_name}` is already being tracked."
            )

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["removeTwitch"])
    @required_configs(ChannelType.TWITCH)
    async def remove_twitch(self, ctx: commands.Context, twitch_login: str) -> None:
        """
        Stop tracking the streams of a given twitch user if already being tracked.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        twitch_user : `str`
            The twitch_username to stop tracking.
        """
        guild_id: int = ctx.guild.id
        twitch_login = twitch_login.lower()

        if twitch_login in self.guild_to_tracked_logins[guild_id]:
            self.client.db.remove_twitch_tracking_data(twitch_login, guild_id)
            del self.twitch_tracking_data[twitch_login][guild_id]
            self.guild_to_tracked_logins[guild_id].remove(twitch_login)

            twitch_user_data: Dict = self.twitch_login_user_data[twitch_login]
            user_id: str = twitch_user_data["id"]
            display_name: str = twitch_user_data["display_name"]
            description: str = twitch_user_data["description"]
            profile_url: str = twitch_user_data["profile_image_url"]
            view_count: int = twitch_user_data["view_count"]

            if len(self.twitch_tracking_data[twitch_login]) == 0:
                self.client.db.remove_twitch_user(twitch_login)
                del self.twitch_login_user_data[twitch_login]

            await ctx.send(f"Twitch user `{display_name}` stopped being tracked.")
            embed = discord.Embed(description=description, color=discord.Color.red())
            embed.set_author(name=display_name, icon_url=profile_url)
            embed.set_thumbnail(url=profile_url)
            embed.add_field(name="Total Viewers", value=view_count, inline=True)
            embed.set_footer(text=f"User ID: {user_id}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"The Twitch user `{twitch_login}` is not being tracked.")

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["listTwitch", "lsTwitch"])
    @required_configs(ChannelType.TWITCH)
    async def list_twitch(self, ctx: commands.Context) -> None:
        """
        List the Twitch streamers being tracked of when their streams go live.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        guild_id: int = ctx.guild.id
        twitch_logins: Set[str] = self.guild_to_tracked_logins[guild_id]
        num_twitch_users: int = len(twitch_logins)
        if num_twitch_users == 0:
            await ctx.send("No Twitch users are currently being tracked")
        else:
            tracking_msg: str = f"__**Tracking {num_twitch_users} Twitch"
            if num_twitch_users == 1:
                tracking_msg += " User:**__\n"
            else:
                tracking_msg += " Users:**__\n"
            tracked_users_msg = "```"
            for twitch_login in twitch_logins:
                display_name: str = self.twitch_login_user_data[twitch_login][
                    "display_name"
                ]
                tracked_users_msg += display_name + ", "
            tracked_users_msg = tracked_users_msg[:-2] + "```"
            tracking_msg += tracked_users_msg
            await ctx.send(tracking_msg)

    @tasks.loop()
    async def check_twitch(self) -> None:
        """
        Sends a message in the #twitch channel when one of the users being tracked
        goes live. Checks every 30 seconds.
        """

        await self.client.wait_until_ready()

        while not self.client.is_closed():
            for twitch_login, guild_map in self.twitch_tracking_data.items():
                stream_response: requests.Response = self.__get_stream_response(
                    twitch_login
                )
                if stream_response.status_code != 200:
                    logger.warning(stream_response.json())
                    continue
                stream_response_data: list = stream_response.json()["data"]
                if not stream_response_data:
                    for guild_id in guild_map:
                        self.twitch_tracking_data[twitch_login][guild_id][
                            "live_message_id"
                        ] = None
                    self.client.db.set_twitch_user_offline(twitch_login)
                    continue

                # ------------- User Data Attributes -------------
                user_data: Dict = self.twitch_login_user_data[twitch_login]
                display_name: str = user_data["display_name"]
                profile_url: str = user_data["profile_image_url"]
                # ------------- Stream Data Attributes --------------
                stream_data: dict = stream_response_data[0]
                stream_id: str = stream_data["id"]
                stream_title: str = stream_data["title"]
                view_count: int = stream_data["viewer_count"]
                started_date: str = stream_data["started_at"]
                thumbnail_url: str = stream_data["thumbnail_url"].replace(
                    "{width}x{height}", "1920x1080"
                )
                # ------------- Game Data Attributes -----------------
                game_id: str = stream_data["game_id"]
                game_response_result: requests.Response = self.__get_game_response(
                    game_id
                )
                if game_response_result.status_code != 200:
                    logger.warning(
                        f"Couldn't find twitch game information for game_id: {game_id}"
                    )
                    continue
                game_name: str = game_response_result.json()["data"][0]["name"]
                for guild_id, tracking_data in guild_map.items():
                    twitch_channel: discord.TextChannel = (
                        self.client.get_twitch_channel(guild_id)
                    )
                    live_message_id: Optional[int] = tracking_data["live_message_id"]
                    # edit existing message
                    if live_message_id:
                        sent_message: discord.Message = (
                            await twitch_channel.fetch_message(live_message_id)
                        )
                        embed_msg: discord.Embed = sent_message.embeds[0]
                        viewer_count: int = int(embed_msg.fields[1].value)
                        # update viewer count if there is an increase
                        if view_count > viewer_count:
                            embed_msg.set_field_at(
                                1, name="Max Viewers", value=view_count
                            )
                            await sent_message.edit(embed=embed_msg)
                    # make new message
                    else:
                        embed = discord.Embed(
                            title=f"{stream_title}",
                            url=f"https://www.twitch.tv/{twitch_login}",
                            timestamp=datetime.strptime(
                                started_date, "%Y-%m-%dT%H:%M:%SZ"
                            ),
                            color=discord.Color.dark_purple(),
                        )
                        embed.set_author(name=display_name, icon_url=profile_url)
                        embed.set_thumbnail(url=profile_url)
                        embed.set_image(url=thumbnail_url)
                        embed.add_field(name="Game", value=game_name, inline=True)
                        embed.add_field(
                            name="Max Viewers", value=view_count, inline=True
                        )
                        member_id: Optional[int] = tracking_data["member_id"]
                        if member_id:
                            member: discord.Member = self.client.get_user(member_id)
                            embed.add_field(
                                name="Member",
                                value=member.mention,
                                inline=True,
                            )
                        embed.set_footer(text=f"Stream ID: {stream_id}")
                        sent_message = await twitch_channel.send(embed=embed)
                        self.client.db.set_twitch_user_live(
                            twitch_login, guild_id, sent_message.id
                        )
                        self.twitch_tracking_data[twitch_login][guild_id][
                            "live_message_id"
                        ] = sent_message.id

                await asyncio.sleep(1)
            await asyncio.sleep(self.TWITCH_CHECK_TIME)


def setup(client):
    client.add_cog(Twitch(client))
