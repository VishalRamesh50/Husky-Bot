import discord
from discord.ext import commands
from typing import List, Dict

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID, ROLES_CHANNEL_ID


class CourseContent(commands.Cog):
    """Commands involved with setup of a new
    course registration page's embedded messages.
    """

    def __init__(self, client: commands.Context):
        self.client = client
        self.dark_mode_color = discord.Color.from_rgb(52, 54, 59)

    async def _send_new_embed(self, ctx: commands.Context, title: str, img_url: str):
        """
        Creates and sends a new embed with the given title and image url.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        title: `str`
            The title of the embed to set.
        img_url: `str`
            The image url to set the embed message's image to.

        Raises
        ------------
        discord.errors.HTTPException: If image url is not valid
        """
        embed = discord.Embed(title=title, color=self.dark_mode_color)
        embed.set_image(url=img_url)
        await ctx.send(embed=embed)

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["newEmbed"])
    async def new_embed(
        self, ctx: commands.Context, img_url: str, *, title: str
    ) -> None:
        """Creates and sends a new embed with the given title and image url.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        img_url: `str`
            The image url to set the embed message's image to.
        title: `str`
            The title of the embed to set.
        """
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            # if invoked from another command the message may not be there to delete anymore
            pass
        try:
            await self._send_new_embed(ctx, title, img_url)
        except discord.errors.HTTPException:
            await ctx.send("Not a valid image url")

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
        try:
            await self._send_new_embed(
                ctx, f"Add/Remove {course_category} courses", img_url
            )
            await ctx.send(
                ":regional_indicator_a: -> Course Description (SampleCourse XXXX)"
            )
        except discord.errors.HTTPException:
            await ctx.send("Not a valid image url")

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
        messages: List[discord.Message] = await (
            COURSE_REGISTRATION_CHANNEL.history(limit=None).filter(
                lambda m: m.embeds and m.embeds[0].title
            )
        ).flatten()
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
            color=discord.Color.red(),
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

        await ctx.send(embed=embed)

    @is_admin()
    @commands.guild_only()
    @commands.command(aliases=["rolesNavEmbed"])
    async def roles_nav_embed(self, ctx: commands.Context) -> None:
        """Sends an navigation link embed linking each role section.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        """
        await ctx.message.delete()

        guild: discord.Guild = ctx.guild
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        ROLES_CHANNEL: discord.TextChannel = guild.get_channel(ROLES_CHANNEL_ID)
        messages: discord.abc.HistoryIterator = ROLES_CHANNEL.history(
            limit=None
        ).filter(lambda m: m.embeds and m.embeds[0].title)

        message_links: List[str] = [message.jump_url async for message in messages]
        color_link, pronouns_link, special_link, school_link, year_link = message_links

        embed = (
            discord.Embed(
                title="Quick Links!",
                description="Jump to each role section by simply clicking on the links below",
                color=discord.Color.red(),
            )
            .add_field(name="Year", value=f"[Click Here]({year_link})")
            .add_field(name="College/School", value=f"[Click Here]({school_link})")
            .add_field(name="Special", value=f"[Click Here]({special_link})")
            .add_field(name="Pronouns", value=f"[Click Here]({pronouns_link})")
            .add_field(name="Colors", value=f"[Click Here]({color_link})")
            .add_field(name="Courses", value=COURSE_REGISTRATION_CHANNEL.mention)
        )
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(CourseContent(client))
