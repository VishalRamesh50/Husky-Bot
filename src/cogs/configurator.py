import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import CategoryChannelConverter, TextChannelConverter
from typing import Callable, Dict, Optional, Tuple, Union

from client.bot import Bot, ChannelType
from checks import is_admin


class Configurator(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @is_admin()
    @commands.guild_only()
    @commands.command()
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
            - Anonymous Mod Mail:
                - NU Guild ID
                - Mod Category
            - Schedules Channel ID
            - Suggestions Channel ID
            - Twitch Channel ID
        Specific Features
        --------------------
            - Bot Spam Channel (Aoun, Help, Icecream, It Be Like That, Misc, Stats, Hours)
            - Onboarding:
                - Course Registration Channel
                - Welcome Channel
                - Roles Channel
                - Not Registered Channel
            - Registration:
                - Course Registration Channel
                - Choose Notification Channel (ADMIN_CHANNEL_ID)
        """

        SETUP_MAP: Dict[str, Tuple[str, Callable]] = {
            "1️⃣": (ChannelType.LOG.value, self._setup_log),
            "2️⃣": (ChannelType.HOF.value, self._setup_hall_of_fame),
            "3️⃣": (ChannelType.MODMAIL.value, self._setup_modmail),
            "4️⃣": (ChannelType.SCHEDULES.value, self._setup_schedules),
            "5️⃣": (ChannelType.SUGGESTIONS.value, self._setup_suggestions),
            "6️⃣": (ChannelType.TWITCH.value, self._setup_twitch),
            "✅": ("All Modules", self.do_nothing),
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
                embed.add_field(name=emoji, value=option_name)
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
                setup_func = SETUP_MAP[str(reaction)][1]
                await setup_func(ctx)
            await ctx.send(
                embed=discord.Embed(
                    title="Setup Complete!",
                    description=f"You can rerun the `{ctx.prefix}setup` command at anytime to change any of these configs.",
                    color=discord.Color.green(),
                )
            )
        except asyncio.TimeoutError:
            await ctx.send(
                embed=discord.Embed(
                    description=f"Timed out. Please use `{ctx.prefix}setup` to try again.",
                    colour=discord.Color.red(),
                )
            )

    async def _setup_template(
        self,
        ctx: commands.Context,
        purpose: str,
        instructions: str,
        channel_type: ChannelType,
        field_name: str,
        is_category: bool = False,
        all_modules: bool = False,
    ):
        """
        Creates an embed with information about the module use and instructions on how
        to configure it.
        Also handles interaction between the user and updates the database and cache.

        Parameters
        -------------
        ctx: `commands.Context`
            A class containing metadata about the command invocation.
        purpose: `str`
            The purpose of the module and why the user should configure it.
        instructions: `str`
            Prompting the user to do something in response to this embed to configure.
        channel_type: `ChannelType`
            The type of channel that is required to setup this module.
        field_name: `str`
            The name of the field which describes the channel/category name to configure.
        is_category: `bool`
            A flag where if True means the module needs to configure a category, else a text channel.
        all_modules: `bool`
            A flag where if True means this was invoked with the intention of setting up all modules.
            This controls whether paginated counts should appear.

        Raises
        --------
        `asyncio.TimeoutError` if the user doesn't respond in time.
        """
        SKIP_EMOJI: str = "⏭"

        def skip_check(reaction: discord.Reaction, user: discord.Member) -> bool:
            return user.id == ctx.author.id and str(reaction) == SKIP_EMOJI

        def msg_check(msg: discord.Message) -> bool:
            return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

        module_step_num: int = list(ChannelType).index(channel_type) + 1
        total_modules: int = len(ChannelType)
        embed = discord.Embed(
            title=f"{channel_type.value} Setup {f'({module_step_num}/{total_modules})' if all_modules else ''}",
            description=f"React with the {SKIP_EMOJI} emoji to skip configuring this module. You can reconfigure this module anytime.",
            color=discord.Color.gold(),
        )
        embed.add_field(name="Module Purpose", value=purpose)
        embed.add_field(name="Instructions", value=instructions)
        embed.add_field(
            name="Notes",
            value="If it doesn't already exist, it will be created and only members with admin permissions will be able to see it.",
        )
        converter = CategoryChannelConverter if is_category else TextChannelConverter
        channel_id: Optional[int] = self.client.channel_config[ctx.guild.id].get(
            channel_type.value
        )
        prev_val: str = "<None>"
        if channel_id:
            try:
                channel: Union[
                    discord.TextChannel, discord.CategoryChannel
                ] = await converter().convert(ctx, str(channel_id))
                prev_val = channel.name if is_category else channel.mention
            except commands.errors.BadArgument:
                pass

        embed.add_field(name=field_name, value=prev_val)
        sent_msg: discord.Message = await ctx.send(embed=embed)
        await sent_msg.add_reaction(SKIP_EMOJI)

        done, pending = await asyncio.wait(
            [
                asyncio.Task(self.client.wait_for("message", timeout=60, check=msg_check)),
                asyncio.Task(self.client.wait_for("reaction_add", timeout=60, check=skip_check)),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        result: Union[
            discord.Message, Tuple[discord.Reaction, discord.User]
        ] = done.pop().result()
        pending.pop().cancel()

        # assume that if a tuple was returned, then this config was skipped
        if isinstance(result, tuple):
            await sent_msg.delete()
            return

        res_msg: discord.Message = result
        try:
            channel = await converter().convert(ctx, res_msg.content)
        except commands.errors.BadArgument:
            create_func: Callable = (
                ctx.guild.create_category
                if is_category
                else ctx.guild.create_text_channel
            )
            channel = await create_func(
                res_msg.content,
                overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        read_messages=False
                    )
                },
            )
        self.client.db.configure_channel(ctx.guild.id, channel_type, channel.id)
        self.client.channel_config[ctx.guild.id][channel_type.value] = channel.id
        embed.set_field_at(
            3, name=field_name, value=channel.name if is_category else channel.mention
        )
        embed.color = discord.Color.green()
        await sent_msg.edit(embed=embed)
        await res_msg.delete()

    async def do_nothing(self, *args, **kwargs):
        pass

    async def _setup_log(self, ctx: commands.Context, all_modules: bool = False):
        await self._setup_template(
            ctx,
            "This is to log all discord related events to a separate log channel.",
            "Please type/mention the name of the channel you want to use.",
            ChannelType.LOG,
            "Log Channel",
            all_modules=all_modules,
        )

    async def _setup_hall_of_fame(
        self, ctx: commands.Context, all_modules: bool = False
    ):
        await self._setup_template(
            ctx,
            "This posts messages which get a certain number of specific reactions in",
            "a designated hall of fame channel for all of its glory.",
            ChannelType.HOF,
            "Hall of Fame",
            all_modules=all_modules,
        )

    async def _setup_modmail(self, ctx: commands.Context, all_modules: bool = False):
        await self._setup_template(
            ctx,
            "This allows members to anonymously raise tickets with the moderation team.",
            "Please type the channel category to put all the opened tickets into.",
            ChannelType.MODMAIL,
            "Ticket Category",
            is_category=True,
            all_modules=all_modules,
        )

    async def _setup_schedules(self, ctx: commands.Context, all_modules: bool = False):
        await self._setup_template(
            ctx,
            "Restricts a specified channel to only send schedules (via attachments).",
            "Please type/mention the channel to restrict to only schedules.",
            ChannelType.SCHEDULES,
            "Schedules Channel",
            all_modules=all_modules,
        )

    async def _setup_suggestions(
        self, ctx: commands.Context, all_modules: bool = False
    ):
        await self._setup_template(
            ctx,
            f"Allows users to make suggestions with the `{ctx.prefix}suggest` command, format, and send them to a specific channel.",
            "Please type/mention the channel to send these suggestions to.",
            ChannelType.SUGGESTIONS,
            "Suggestions Channel",
            all_modules=all_modules,
        )

    async def _setup_twitch(self, ctx: commands.Context, all_modules: bool = False):
        await self._setup_template(
            ctx,
            "Allows the bot to notify when certain Twitch channels are live.",
            "Please type/mention the channel to send these notifications to.",
            ChannelType.TWITCH,
            "Twitch Channel",
            all_modules=all_modules,
        )


async def setup(client):
    await client.add_cog(Configurator(client))
