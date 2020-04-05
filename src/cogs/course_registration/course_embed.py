import discord
from discord.ext import commands
from typing import List, Dict

from checks import is_admin
from data.ids import COURSE_REGISTRATION_CHANNEL_ID


class CourseEmbed(commands.Cog):
    def __init__(self, client: commands.Context):
        self.client = client

    @is_admin()
    @commands.guild_only()
    @commands.command()
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
    @commands.command()
    async def edit_embed_image(
        self, ctx, message: discord.Message, img_url: str
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
    @commands.command()
    async def edit_embed_title(
        self, ctx, message: discord.Message, *title_parts
    ) -> None:
        """Edits the title for all the embedded messages
        in the given message to the given title.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        message: `discord.Message`
            The message to edit.
        title_parts: Tuple
            The new title as a tuple of strings.
        """
        await ctx.message.delete()
        title: str = " ".join(title_parts)
        for embed in message.embeds:
            embed.title = title
            await message.edit(embed=embed)
        await ctx.send(f"Title for message `{message.id}` was edited")

    @is_admin()
    @commands.guild_only()
    @commands.command()
    async def edit_course_content(
        self, ctx: commands.Context, message: discord.Message, *content_parts
    ) -> None:
        """Edits the content of the message use '\n' to indicate newline.
        Will not edit a message if it has embeds.

        Parameters
        ------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        message: `discord.Message`
            The message to edit.
        content_parts: Tuple
            The new message content as a tuple of strings.
        """

        await ctx.message.delete()
        if message.embeds:
            await ctx.send(
                "You accidentally tried to edit the embedded message", delete_after=5
            )
            return

        content_list: List[str] = " ".join(content_parts).split("\\n")
        content: str = "\n".join(content_list)
        await message.edit(content=content)
        await ctx.send(f"Content for message `{message.id}` was edited")

    # sends a new embedded msg with the given title and image url
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def navEmbed(self, ctx):
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
        # get all the messages in course-registration
        messages: List[discord.Message] = await COURSE_REGISTRATION_CHANNEL.history(limit=None).flatten()
        # filter out all the messages which don't have embeds or a title
        messages = list(filter(lambda x: x.embeds and x.embeds[0].title, messages))
        # sort the messages by their embed's title
        messages.sort(key=lambda m: (m.embeds[0].title))
        letter_to_link: Dict[str, str] = {}
        # assign a letter to the first jump_link of a message
        for message in messages:
            course: str = message.embeds[0].title.replace('Add/Remove ', '')
            starting_letter: str = course[0]
            # if the course starting with the letter has not been added yet
            if letter_to_link.get(starting_letter) is None:
                letter_to_link[starting_letter] = message.jump_url

        alpha_links: str = ""
        # Each letter has it's own thing
        for letter, link in letter_to_link.items():
            alpha_links += f"[{letter}]({link}) **|** "

        # remove the trailing divider
        alpha_links = alpha_links[:-7]
        try:
            embed = discord.Embed(
                title="Quick Links!",
                description=f"Jump to each course category starting with the given letter by simply clicking on the links below\n{alpha_links}",
                colour=discord.Colour.red()
            )
        # if there are too many characters in the description
        except 400 as e:
            print(type(e))
            print(e)
            embed = discord.Embed(
                title="Quick Links!",
                description=f"Jump to each course category starting with the given letter by simply clicking on the links below",
                colour=discord.Colour.red()
            )
            # Divide by the middle for 2 groups
            # 7 links is about the most a field can hold
            middle: int = min(len(letter_to_link) // 2, 7)
            counter: int = 0
            for key, val in letter_to_link.items():
                alpha_links += f"[{key}]({val}) "
                counter += 1
                if counter % middle == 0 or counter == len(letter_to_link):
                    embed.add_field(name=f"{alpha_links[1]}-{key}", value=alpha_links, inline=True)

        top_messages: List[discord.Message] = await COURSE_REGISTRATION_CHANNEL.history(limit=4, oldest_first=True).flatten()
        embed.add_field(name=f"Top Of Page", value=f"[Pick School/Major Here]({top_messages[0].jump_url})", inline=True)
        embed.add_field(name=f"Colors", value=f"[Choose Colors Here]({top_messages[2].jump_url})", inline=True)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(CourseEmbed(client))
