import asyncio
import discord
import os
import pymongo
import requests
from datetime import datetime
from discord.ext import commands
from typing import Optional

from data.ids import TWITCH_CHANNEL_ID

TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
DB_CONNECTION_URL = os.environ["DB_CONNECTION_URL"]

# connect to mongodb cluster
mongoClient = pymongo.MongoClient(DB_CONNECTION_URL)
db = mongoClient.twitch  # use the twitch database


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
    def __init__(self, client: commands.Bot):
        self.client = client
        self.TWITCH_CHECK_TIME = 30
        self.client.loop.create_task(self.check_twitch())  # iniate loop for twitch notifs

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
        return requests.get(f'https://api.twitch.tv/helix/users?login={login}',
                            headers={'Client-ID': TWITCH_CLIENT_ID})

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
        return requests.get(f'https://api.twitch.tv/helix/streams?user_login={login}',
                            headers={'Client-ID': TWITCH_CLIENT_ID})

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
        return requests.get(f'https://api.twitch.tv/helix/games?id={game_id}',
                            headers={'Client-ID': TWITCH_CLIENT_ID})

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addTwitch(self, ctx: commands.Context, twitch_user: str, member: discord.Member = None) -> None:
        """
        Adds a twitch user to track and send notifications for when they go live.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        twitch_user : `str`
            The twitch_username to track.
        """
        user_response: requests.Response = self.__get_user_response(twitch_user)
        user_data: list = user_response.json()["data"]
        # if the user isn't a valid Twitch user
        if not user_data:
            await ctx.send(f"No Twitch user `{twitch_user}` found.")
            return

        user_data: dict = user_data[0]
        user_data["discord_user_id"]: Optional[int] = member.id if member else None
        # ------------- User Data Attributes --------------
        user_id: str = user_data["id"]
        login: str = user_data["login"]
        display_name: str = user_data["display_name"]
        description: str = user_data["description"]
        profile_url: str = user_data["profile_image_url"]
        view_count: int = user_data["view_count"]
        # -------------------------------------------------

        # if the given Twitch user is not already in the database
        if not db.twitch_users.find_one({"login": login}):
            db.twitch_users.insert_one(user_data)
            await ctx.send(f"Started to track Twitch user `{display_name}`.")
            embed = discord.Embed(
                description=description,
                colour=discord.Colour.dark_purple()
            )
            embed.set_author(name=display_name, icon_url=profile_url)
            embed.set_thumbnail(url=profile_url)
            embed.add_field(name="Total Viewers", value=view_count, inline=True)
            embed.set_footer(text=f"User ID: {user_id}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"The Twitch user `{display_name}` is already being tracked.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeTwitch(self, ctx: commands.Context, twitch_user: str) -> None:
        """
        Stop tracking the streams of a given twitch user if already being tracked.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        twitch_user : `str`
            The twitch_username to stop tracking.
        """
        user_response: requests.Response = self.__get_user_response(twitch_user)
        user_data: list = user_response.json()["data"]
        # if the user isn't a valid Twitch user
        if not user_data:
            await ctx.send(f"No Twitch user `{twitch_user}` found.")
            return

        user_data: dict = user_data[0]
        # ------------- User Data Attributes -------------
        user_id: str = user_data["id"]
        login: str = user_data["login"]
        display_name: str = user_data["display_name"]
        description: str = user_data["description"]
        profile_url: str = user_data["profile_image_url"]
        view_count: int = user_data["view_count"]
        # -------------------------------------------------

        db.live_streams.remove({"user_id": user_id})
        # if the given Twitch user is not already in the database
        if not db.twitch_users.find_one({"login": login}):
            await ctx.send(f"The Twitch user `{display_name}` is not being tracked.")
        else:
            db.twitch_users.remove({"login": login})
            await ctx.send(f"Twitch user `{display_name}` stopped being tracked.")
            embed = discord.Embed(
                description=description,
                colour=discord.Colour.red()
            )
            embed.set_author(name=display_name, icon_url=profile_url)
            embed.set_thumbnail(url=profile_url)
            embed.add_field(name="Total Viewers", value=view_count, inline=True)
            embed.set_footer(text=f"User ID: {user_id}")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listTwitch(self, ctx: commands.Context) -> None:
        """
        List the Twitch streamers being tracked of when their streams go live.

        Parameters
        ----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        num_twitch_users: int = db.twitch_users.count()
        tracking_msg: str = f"__**Tracking {num_twitch_users} Twitch"
        if num_twitch_users == 1:
            tracking_msg += " User:**__"
        else:
            tracking_msg += " Users:**__"
        tracked_users_msg = "```"
        for user in db.twitch_users.find():
            tracked_users_msg += user["display_name"] + ", "
        tracked_users_msg = tracked_users_msg[:-2] + "```"
        await ctx.send(tracking_msg)
        await ctx.send(tracked_users_msg)

    async def check_twitch(self) -> None:
        """
        Sends a message in the #twitch Discord channel when one of the users being tracked
        goes live. Checks every 30 seconds.
        """
        await self.client.wait_until_ready()

        while not self.client.is_closed():
            TWITCH_CHANNEL: discord.Channel = self.client.get_channel(TWITCH_CHANNEL_ID)
            for user_data in db.twitch_users.find():
                # ------------- User Data Attributes -------------
                login: str = user_data["login"]
                display_name: str = user_data["display_name"]
                profile_url: str = user_data["profile_image_url"]
                discord_user_id: Optional[int] = user_data["discord_user_id"]
                # -------------------------------------------------
                stream_response: requests.Response = self.__get_stream_response(login)
                stream_data: list = stream_response.json()["data"]
                # if this user is streaming now
                if stream_data:
                    # ------------- Stream Data Attributes --------------
                    stream_data: dict = stream_data[0]
                    stream_id = stream_data["id"]
                    stream_title: str = stream_data["title"]
                    view_count: str = stream_data["viewer_count"]
                    started_date: str = stream_data["started_at"]
                    thumbnail_url: str = stream_data["thumbnail_url"].replace("{width}x{height}", "1920x1080")
                    # ------------- Game Data Attributes -----------------
                    game_id: str = stream_data["game_id"]
                    game_result: requests.Response = self.__get_game_response(game_id)
                    game_name: str = game_result.json()["data"][0]["name"]
                    # ----------------------------------------------------
                    # if a message has not already been sent saying this member went live
                    if not db.live_streams.find_one({"user_name": display_name}):
                        db.live_streams.insert_one(stream_data)
                        embed = discord.Embed(
                            title=f"{stream_title}",
                            url=f"https://www.twitch.tv/{login}",
                            timestamp=datetime.strptime(started_date, "%Y-%m-%dT%H:%M:%SZ"),
                            colour=discord.Colour.dark_purple()
                        )
                        embed.set_author(name=display_name, icon_url=profile_url)
                        embed.set_thumbnail(url=profile_url)
                        embed.set_image(url=thumbnail_url)
                        embed.add_field(name="Game", value=game_name, inline=True)
                        embed.add_field(name="Viewers", value=view_count, inline=True)
                        if discord_user_id:
                            discord_member: discord.Member = self.client.get_user(discord_user_id)
                            embed.add_field(name="Member", value=discord_member.mention, inline=True)
                        embed.set_footer(text=f"Stream ID: {stream_id}")
                        await TWITCH_CHANNEL.send(embed=embed)
                # if the user is not live
                else:
                    db.live_streams.remove({"user_name": display_name})
            await asyncio.sleep(self.TWITCH_CHECK_TIME)


def setup(client):
    client.add_cog(Twitch(client))
