import discord
from discord.ext import commands


class NewSemester(commands.Cog):
    def __init__(self, client):
        self.client = client

    # removes all course roles from every member
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newSemester(self, ctx):
        await ctx.send("Goodbye courses...")
        for member in ctx.guild.members:
            rolesToRemove = list(filter(lambda r: '-' in r.name, member.roles))
            await member.remove_roles(*rolesToRemove)
        await ctx.send("No classes! WOO!")

    # sends a new embedded msg with the given title and image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def newEmbed(self, ctx, *args):
        title = ""
        url = ""
        for word in args:
            if "http" in word:
                url += word
            else:
                title += word.strip() + ' '
        embed = discord.Embed(
            title=title,
            colour=discord.Color.from_rgb(52, 54, 59)
        )
        try:
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        except discord.errors.HTTPException:
            await ctx.send(f"Not a valid image url")

    # edits the images for all the embedded messages in the given msg to the given image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editEmbedImage(self, ctx, message: discord.Message, url):
        for embed in message.embeds:
            try:
                embed.set_image(url=url)
                await message.edit(embed=embed)
                await ctx.send(f"Image for `{embed.title}` was edited")
            except discord.errors.HTTPException:
                await ctx.send("Not a valid image url")

    # edits the title for all the embedded messages in the given msg to the given title
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editTitle(self, ctx, message: discord.Message, *args):
        title = ' '.join(args)
        for embed in message.embeds:
            embed.title = title
            await message.edit(embed=embed)
            await ctx.send(f"Title for message `{message.id}` was edited")


def setup(client):
    client.add_cog(NewSemester(client))
