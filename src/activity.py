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
        userInput = ' '.join(args).upper()  # user's argument as one string
        matches = []  # list of members who are doing the given activity
        img = None  # an image for the activity
        if userInput != '':
            # get the special characters from the userInput
            specialChars = self.getSpecialChars(userInput)
            # for each member in the guild
            for member in guild.members:
                for activity in member.activities:
                    name = activity.name.upper()
                    # split name by special characters except for the given specialChars
                    name = re.split('[^{}{}]'.format(specialChars, r"\w"), name)
                    name = [x.strip() for x in name]  # strips all the whitespace from each item
                    # generates an abbreviation for each game by using the first letters of each word
                    # and including the given specialChars
                    abbreviation = ''.join([x[0] + self.getSpecialChars(x) if len(x) > 0 else '' for x in name])
                    # if the given activity matches the activity of a user
                    if set(userInput.split()).issubset(set(name)) or ((len(abbreviation) > 1) and userInput == abbreviation):
                        # if a user is listening to Spotify
                        if activity.name == 'Spotify':
                            img = 'https://developer.spotify.com/assets/branding-guidelines/icon3@2x.png'
                        else:
                            # if the img has not been set yet
                            if img is None and not isinstance(activity, discord.activity.Game):
                                img = activity.large_image_url
                        matches.append(member)

            try:
                embed = discord.Embed(
                    description=f'**{len(matches)} Members playing "{userInput}"!**',
                    timestamp=EST,
                    colour=discord.Colour.green()
                )
                # set an thumbnail if an img exists
                if img:
                    embed.set_thumbnail(url=img)
                for member in matches:
                    embed.add_field(name=member.name, value=member.mention, inline=True)
                await ctx.send(embed=embed)
            except discord.errors.HTTPException as e:
                print(e)

    # find the people streaming right now
    @commands.command()
    async def streaming(self, ctx):
        EST = datetime.now(timezone('US/Eastern'))  # EST timezone
        pairs = []
        guild = ctx.guild
        for member in guild.members:
            activity = member.activity
            if activity:
                if activity.type == discord.ActivityType.streaming:
                    pairs.append({'steam_name': activity.name, 'url': activity.url, 'details': activity.details, 'pic': activity.small_image_url})

        embed = discord.Embed(
            description=f"**{len(pairs)} members streaming right now!**",
            timestamp=EST,
            colour=discord.Colour.purple()
        )
        for dict in pairs:
            stream_name = dict['stream_name']
            url = dict['url']
            details = dict['details']
            pic = dict['pic']
            embed.add_field(name='Stream Name', value=f"[{stream_name}]({url})", inline=False)
            embed.add_field(name='Details', value=details, inline=False)
            embed.add_field(name='Pic', value=pic, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Activity(client))
