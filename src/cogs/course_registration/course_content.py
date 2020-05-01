import discord
from discord.ext import commands
from typing import List, Dict

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID


class CourseContent(commands.Cog):
    """Commands involved with setup of a new
    course registration page's embedded messages.
    """

    def __init__(self, client: commands.Context):
        self.client = client

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["courseEmbed", "newCourseEmbed"])
    async def course_embed(
        self, ctx: commands.Context, course_category: str, img_url: str
    ) -> None:
        """Sends a new embedded message indicating which category this embedded message
        would have reaction roles associated with and sets the embed image with the
        given image url.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        course_category: `str`
            The course category to create the embedded message for.
        img_url: `str`
            The image url to set the embed message's image to.
        """
        await ctx.message.delete()
        embed = discord.Embed(
            title=f"Add/Remove {course_category} courses",
            colour=discord.Color.from_rgb(52, 54, 59),
        )
        try:
            embed.set_image(url=img_url)
            await ctx.send(embed=embed)
            await ctx.send(
                ":regional_indicator_a: -> Course Description (SampleCourse XXXX)"
            )
        except discord.errors.HTTPException:
            await ctx.send(f"Not a valid image url")

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["editEmbedImage"])
    async def edit_embed_image(
        self, ctx: commands.Context, message: discord.Message, img_url: str
    ) -> None:
        """Edits the images for all the embedded messages
        in the given message to the given image url.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        message: `discord.Message`
            The message to edit.
        img_url: `str`
            The image url to to set the image for the embedded message.
        """
        await ctx.message.delete()
        for embed in message.embeds:
            try:
                embed.set_image(url=img_url)
                await message.edit(embed=embed)
                await ctx.send(f"Image for `{embed.title}` was edited")
            except discord.errors.HTTPException:
                await ctx.send("Not a valid image url")

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["editEmbedTitle"])
    async def edit_embed_title(
        self, ctx, message: discord.Message, *, title: str
    ) -> None:
        """Edits the title for all the embedded messages
        in the given message to the given title.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        message: `discord.Message`
            The message to edit.
        title: `str`
            The new title.
        """
        await ctx.message.delete()
        for embed in message.embeds:
            embed.title = title
            await message.edit(embed=embed)
        await ctx.send(f"Title for message `{message.id}` was edited")

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["editCourseContent"])
    async def edit_course_content(
        self, ctx: commands.Context, message: discord.Message, *, content
    ) -> None:
        """Edits the content of the message to the new content.
        Will not edit a message if it has embeds.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        message: `discord.Message`
            The message to edit.
        content: `str`
            The new message content.
        """
        await ctx.message.delete()
        if message.embeds:
            await ctx.send(
                "You accidentally tried to edit the embedded message", delete_after=5
            )
            return

        await message.edit(content=content)
        await ctx.send(f"Content for message `{message.id}` was edited")

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["navEmbed"])
    async def nav_embed(self, ctx: commands.Context) -> None:
        """Sends an navigation link embed linking to the first category message for each
        letter in the alphabet. Also has links to select a major and change colors.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        guild: discord.Guild = ctx.guild
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        messages: List[discord.Message] = (
            await (
                COURSE_REGISTRATION_CHANNEL.history(limit=None).filter(
                    lambda m: m.embeds and m.embeds[0].title
                )
            ).flatten()
        )[:-1]
        messages.sort(key=lambda m: m.embeds[0].title)

        letter_to_link: Dict[str, str] = {}
        for message in messages:
            starting_letter: str = message.embeds[0].title.replace("Add/Remove ", "")[0]
            if letter_to_link.get(starting_letter) is None:
                letter_to_link[starting_letter] = message.jump_url

        alpha_links: str = ""
        for letter, link in letter_to_link.items():
            alpha_links += f"[{letter}]({link}) **|** "
        alpha_links = alpha_links[:-7]

        embed = discord.Embed(
            title="Quick Links!",
            description=f"Jump to each course category starting with the given letter by simply clicking on the links below\n{alpha_links}",
            colour=discord.Colour.red(),
        )
        if len(embed.description) > 2048:
            embed.description = "Jump to each course category starting with the given letter by simply clicking on the links below"
            # Divide by the middle for 2 groups. 7 links is about the most a field can hold
            middle: int = min(len(letter_to_link) // 2, 7)
            counter: int = 0
            for key, val in letter_to_link.items():
                alpha_links += f"[{key}]({val}) "
                counter += 1
                if counter % middle == 0 or counter == len(letter_to_link):
                    embed.add_field(name=f"{alpha_links[1]}-{key}", value=alpha_links)

        top_messages: List[discord.Message] = await COURSE_REGISTRATION_CHANNEL.history(
            limit=4, oldest_first=True
        ).flatten()
        embed.add_field(
            name=f"Top Of Page",
            value=f"[Pick School/Major Here]({top_messages[0].jump_url})",
        )
        embed.add_field(
            name=f"Colors", value=f"[Choose Colors Here]({top_messages[2].jump_url})",
        )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(CourseContent(client))
