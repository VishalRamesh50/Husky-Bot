import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import CategoryChannelConverter, TextChannelConverter
from typing import Callable, Dict, Tuple

from checks import is_admin


class Configurator(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def setup(self, ctx: commands.Context) -> None:
        """
        General Features
        ------------------
            - Log Channel ID
            - Hall of Fame:
                Blacklist:
                    - Announcements Channel
                    - Course Registration Channel
                    - HOF Channel
                    - Rules Channel
            - Anonymous Mod Mail:
                - NU Guild ID
                - Mod Category
            - Schedules Channel ID
            - Suggestions Channel ID
            - Twitch Channel ID
        Specific Features
        --------------------
            - Bot Spam Channel (Aoun, Help, Icecream, It Be Like That, Misc, Stats, Hours)
            - April Fools
                - NU Guild ID
                - Not Registered Role ID
            - Onboarding:
                - Course Registration Channel
                - Welcome Channel
                - Rules Channel
                - Not Registered Channel
                - Not Registered Role
            - Registration:
                - Course Registration Channel
                - Choose Notification Channel (ADMIN_CHANNEL_ID)
        """

        SETUP_MAP: Dict[str, Tuple[str, Callable]] = {
            "1️⃣": ("Action Log", self._setup_log),
            "2️⃣": ("Anonymous Modmail", self._setup_modmail),
            "3️⃣": ("Schedules", self._setup_schedules),
            "4️⃣": ("Suggestions", self._setup_suggestions),
            "5️⃣": ("Twitch", self._setup_twitch),
            "✅": ("All of the Above", asyncio.coroutine(lambda *args, **kwargs: None)),
        }

        def check(reaction: discord.Reaction, user: discord.Member) -> bool:
            return user.id == ctx.author.id and str(reaction) in SETUP_MAP

        try:
            embed = discord.Embed(
                title="Setup Modules",
                description="This will walk you through setting up all the custom channels and roles"
                " you will need in order to take advantage of all the features. React with the respective "
                "emoji to setup that module.",
                colour=discord.Color.red(),
            )
            for emoji, (option_name, _) in SETUP_MAP.items():
                embed.add_field(name=emoji, value=option_name, inline=False)
            sent_msg: discord.Message = await ctx.send(embed=embed)
            for emoji in SETUP_MAP:
                await sent_msg.add_reaction(emoji)
            reaction, _ = await self.client.wait_for(
                "reaction_add", timeout=60, check=check
            )
            all_modules: bool = str(reaction) == "✅"
            if all_modules:
                for _, setup_func in SETUP_MAP.values():
                    await setup_func(ctx, all_modules=True)
            else:
                await SETUP_MAP[str(reaction)][1](ctx)
        except asyncio.TimeoutError:
            await ctx.send(
                embed=discord.Embed(
                    description=f"Timed out. Please use `{ctx.prefix}setup` to try again.",
                    colour=discord.Color.red(),
                )
            )

    async def _setup_log(self, ctx: commands.Context, all_modules: bool = False):
        def check(msg: discord.Message) -> bool:
            return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

        embed = discord.Embed(
            title=f"Action Log Setup {'(1/5)' if all_modules else ''}",
            description="This is to log all discord related events to a separate log channel.\n"
            "Please type/mention the name of the channel you want to use.\n"
            "If it doesn't already exist, it will be created and only members with admin permissions will be able to see it.",
            color=discord.Color.gold(),
        )
        # TODO: Fill this in with what the previous channel was if it existed, otherwise default it to something
        embed.add_field(name="Log Channel", value="<None>")
        sent_msg: discord.Message = await ctx.send(embed=embed)
        res_msg: discord.Message = await self.client.wait_for(
            "message", timeout=60, check=check
        )
        try:
            log_channel: discord.TextChannel = await TextChannelConverter().convert(
                ctx, res_msg.content
            )
        except commands.errors.BadArgument:
            log_channel = await ctx.guild.create_text_channel(
                res_msg.content,
                overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        read_messages=False
                    )
                },
            )
        # TODO: Update db and cache
        embed.set_field_at(0, name="Log Channel", value=log_channel.mention)
        embed.color = discord.Color.green()
        await sent_msg.edit(embed=embed)
        await res_msg.add_reaction("✅")

    async def _setup_modmail(self, ctx: commands.Context, all_modules: bool = False):
        def check(msg: discord.Message) -> bool:
            return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

        embed = discord.Embed(
            title=f"Anonymous Modmail Setup {'(2/5)' if all_modules else ''}",
            description="This allows members to anonymously raise tickets with the moderation team.\n"
            "Please type the channel category to put all the opened tickets into.\n"
            "If it doesn't already exist, it will be created and only members with admin permissions will be able to see it.",
            color=discord.Color.gold(),
        )
        # TODO: Fill this in with what the previous category was if it existed, otherwise default it to something
        embed.add_field(name="Ticket Category", value="<None>")
        sent_msg: discord.Message = await ctx.send(embed=embed)
        res_msg: discord.Message = await self.client.wait_for(
            "message", timeout=60, check=check
        )
        try:
            ticket_category: discord.CategoryChannel = await CategoryChannelConverter().convert(
                ctx, res_msg.content
            )
        except commands.errors.BadArgument:
            ticket_category = await ctx.guild.create_category(
                res_msg.content,
                overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        read_messages=False
                    )
                },
            )
        # TODO: Update db and cache
        embed.set_field_at(0, name="Ticket Category", value=ticket_category.name)
        embed.color = discord.Color.green()
        await sent_msg.edit(embed=embed)
        await res_msg.add_reaction("✅")

    async def _setup_schedules(self, ctx: commands.Context, all_modules: bool = False):
        def check(msg: discord.Message) -> bool:
            return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

        embed = discord.Embed(
            title=f"Schedules Setup {'(3/5)' if all_modules else ''}",
            description="Restricts a specified channel to only allow attachments. Ideal for posting schedules.\n"
            "Please type/mention the channel to restrict to schedules only all the opened tickets into.\n"
            "If it doesn't already exist, it will be created and only members with admin permissions will be able to see it.",
            color=discord.Color.gold(),
        )
        # TODO: Fill this in with what the previous category was if it existed, otherwise default it to something
        embed.add_field(name="Schedules Channel", value="<None>")
        sent_msg: discord.Message = await ctx.send(embed=embed)
        res_msg: discord.Message = await self.client.wait_for(
            "message", timeout=60, check=check
        )
        try:
            schedules_channel: discord.TextChannel = await TextChannelConverter().convert(
                ctx, res_msg.content
            )
        except commands.errors.BadArgument:
            schedules_channel = await ctx.guild.create_category(
                res_msg.content,
                overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        read_messages=False
                    )
                },
            )
        # TODO: Update db and cache
        embed.set_field_at(0, name="Schedules Channel", value=schedules_channel.name)
        embed.color = discord.Color.green()
        await sent_msg.edit(embed=embed)
        await res_msg.add_reaction("✅")

    async def _setup_suggestions(
        self, ctx: commands.Context, all_modules: bool = False
    ):
        def check(msg: discord.Message) -> bool:
            return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

        embed = discord.Embed(
            title=f"Suggestions Setup {'(4/5)' if all_modules else ''}",
            description=f"The channel where suggestions made with the `{ctx.prefix}suggest` command go.\n"
            "Please type/mention the channel to send these suggestions to.\n"
            "If it doesn't already exist, it will be created and only members with admin permissions will be able to see it.",
            color=discord.Color.gold(),
        )
        # TODO: Fill this in with what the previous category was if it existed, otherwise default it to something
        embed.add_field(name="Suggestions Channel", value="<None>")
        sent_msg: discord.Message = await ctx.send(embed=embed)
        res_msg: discord.Message = await self.client.wait_for(
            "message", timeout=60, check=check
        )
        try:
            suggestions_channel: discord.TextChannel = await TextChannelConverter().convert(
                ctx, res_msg.content
            )
        except commands.errors.BadArgument:
            schedules_channel = await ctx.guild.create_category(
                res_msg.content,
                overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        read_messages=False
                    )
                },
            )
        # TODO: Update db and cache
        embed.set_field_at(
            0, name="Suggestions Channel", value=suggestions_channel.name
        )
        embed.color = discord.Color.green()
        await sent_msg.edit(embed=embed)
        await res_msg.add_reaction("✅")

    async def _setup_twitch(self, ctx: commands.Context, all_modules: bool = False):
        pass


def setup(client):
    client.add_cog(Configurator(client))
