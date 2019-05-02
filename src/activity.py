import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone


class Activity(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.EST = datetime.now(timezone('US/Eastern'))  # EST timezone

    # find the people playing a certain activity
    @commands.command()
    async def playing(self, ctx, *args):
        self.__init__(self.client)  # re-initialize variables
        guild = ctx.guild
        userActivity = ' '.join(args).upper()  # user's argument as one string
        pairs, img = [], None
        # for each member in the guild
        for member in guild.members:
            activity = member.activity
            # if they are performing an activity
            if activity:
                name = activity.name.upper()
                # if the given activity matches the activity of a user
                if userActivity in name and userActivity != '':
                    # if a user is listening to Spotify
                    if activity.type == discord.ActivityType.listening:
                        img = 'https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png'
                    else:
                        # if the img has not been set yet
                        if img is None and not isinstance(activity, discord.activity.Game):
                            img = activity.large_image_url
                    pairs.append({'name': member.name, 'mention': member.mention})

        embed = discord.Embed(
            description=f"**{len(pairs)} Members playing {userActivity}!**",
            timestamp=self.EST,
            colour=discord.Colour.green()
        )
        # set an thumbnail if an img exists
        if img:
            embed.set_thumbnail(url=img)
        for dict in pairs:
            embed.add_field(name=dict['name'], value=dict['mention'], inline=True)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Activity(client))
