import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone
import re


class Activity(commands.Cog):
    def __init__(self, client):
        self.client = client

    def getSpecialChars(self, name):
        result = ''
        for char in name:
            if not char.isalnum():
                result += char
        return result

    # find the people playing a certain activity
    @commands.command()
    async def playing(self, ctx, *args):
        EST = datetime.now(timezone('US/Eastern'))  # EST timezone
        guild = ctx.guild
        userActivity = ' '.join(args).upper()  # user's argument as one string
        pairs, img = [], None
        # get the special characters from the userActivity
        specialChars = self.getSpecialChars(userActivity)
        # for each member in the guild
        for member in guild.members:
            activity = member.activity
            # if member is performing an activity
            if activity:
                name = activity.name.upper()
                # split name by special characters except for the given specialChars and then rejoin
                name = re.split('[^{}{}]'.format(specialChars, r"\w"), name)
                # if the given activity matches the activity of a user
                if userActivity in name and userActivity != '':
                    # if a user is listening to Spotify
                    if userActivity == 'SPOTIFY':
                        img = 'https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png'
                    else:
                        # if the img has not been set yet
                        if img is None and not isinstance(activity, discord.activity.Game):
                            img = activity.large_image_url
                    pairs.append({'name': member.name, 'mention': member.mention})

        try:
            embed = discord.Embed(
                description=f"**{len(pairs)} Members playing {userActivity}!**",
                timestamp=EST,
                colour=discord.Colour.green()
            )
            # set an thumbnail if an img exists
            if img:
                embed.set_thumbnail(url=img)
            for dict in pairs:
                embed.add_field(name=dict['name'], value=dict['mention'], inline=True)
            await ctx.send(embed=embed)
        except discord.errors.HTTPException as e:
            print(e)


def setup(client):
    client.add_cog(Activity(client))
