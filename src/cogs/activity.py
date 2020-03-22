import discord
import re
from datetime import datetime
from discord.ext import commands
from typing import Dict, List, Optional


class Activity(commands.Cog):
    """Controls all things related to Discord Activity Detection."""

    def __init__(self, client: commands.Bot):
        self.client = client

    def __get_special_chars(self, name: str) -> str:
        """Returns all the special characters in the given string as a string.

        Parameters
        ------------
        name: `str`
            The given string to process.

        Returns
        ---------
        A string containing all the special characters in the given string.
        Whitespace does not count as a special character.
        """

        match_special_chars = re.compile(r"[^ \w]")
        return "".join(match_special_chars.findall(name))

    def __activity_match(self, user_input: str, user_activity: str) -> bool:
        """Determines if the given user input is equivalent to the user activity name.

        Parameters
        ------------
        user_input: `str`
            The user input to compare from. This is assumed to either be a full
            activity name or an acronym.
        user_activity: `str`
            This is the name of the activity to compare the user_input to.

        Returns
        --------
        True if the user_input is found to be a match to the user_activity, else False.
        """

        CUSTOM_ACRONYMS: Dict[str, str] = {
            "VS CODE": "VISUAL STUDIO CODE",
            "PUBG": "PLAYERUKNOWNSBATTLEGROUNDS",
        }
        user_input = user_input.upper()
        user_activity = user_activity.upper()
        user_input_special_chars: str = self.__get_special_chars(user_input)
        # split name by special characters except for the given specialChars
        user_activity_split: List[str] = [
            x for x in re.split(fr"[^{user_input_special_chars}\w]", user_activity) if x
        ]
        # if the search term is found within the user activity
        if set(user_activity_split).issuperset(set(user_input.split())):
            return True
        user_activity_acronym = "".join(
            [x[0] + self.__get_special_chars(x) for x in user_activity_split]
        )
        # if the search term is an acronym which is within the acronym of the user activity
        if len(user_input) > 0 and user_input in user_activity_acronym:
            return True
        # if the user input is an custom acronym which matches the user activity
        return CUSTOM_ACRONYMS.get(user_input) == user_activity

    @commands.command()
    async def playing(self, ctx: commands.Context, *args) -> None:
        """Sends an embedded message containg all the people playing the
        asked activity.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        args: `Tuple`
            A tuple of arguments that the user sends which will be built up
            to represent the name of the activity to search for.
        """

        user_input: str = " ".join(args)
        print(f'"{user_input}"')
        if user_input == "":
            await ctx.send("You didn't pick an activity!", delete_after=5)
            return

        guild: discord.Guild = ctx.guild
        # an image for the activity
        img: Optional[str] = None

        embed = discord.Embed(
            timestamp=datetime.utcnow(), colour=discord.Colour.green(),
        )

        count: int = 0
        for member in guild.members:
            activities = filter(
                lambda a: not isinstance(a, discord.CustomActivity), member.activities
            )
            for activity in activities:
                if self.__activity_match(user_input, activity.name):
                    count += 1
                    embed.add_field(name=member.name, value=member.mention, inline=True)
                    if isinstance(activity, discord.Spotify):
                        img = "https://developer.spotify.com/assets/branding-guidelines/icon3@2x.png"
                    else:
                        if img is None and isinstance(activity, discord.Activity):
                            img = activity.large_image_url

        embed.description = f'**{count} Member(s) playing "{user_input}"!**'
        if img:
            embed.set_thumbnail(url=img)
        await ctx.send(embed=embed)

    @commands.command()
    async def streaming(self, ctx: commands.Context) -> None:
        """Sends an embedded message of all the people streaming currently.

        Parameters
        -----------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        embed = discord.Embed(
            timestamp=datetime.utcnow(), colour=discord.Colour.purple(),
        )
        count: int = 0
        guild = ctx.guild
        for member in guild.members:
            for activity in member.activities:
                if activity.type == discord.ActivityType.streaming:
                    embed.add_field(name=member.name, value=member.mention, inline=True)
                    count += 1
                    break

        embed.description = f"**{count} Member(s) streaming right now!**"
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Activity(client))
