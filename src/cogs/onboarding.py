import discord
from discord.ext import commands
from typing import List, Optional

from data.ids import (
    COURSE_REGISTRATION_CHANNEL_ID,
    NOT_REGISTERED_CHANNEL_ID,
    ROLES_CHANNEL_ID,
    WELCOME_CHANNEL_ID,
)


class Onboarding(commands.Cog):
    """Handles the onboarding experience for new members who join.

    A member who joins will have access to a limited amount of channels until they register.
    After a member has gained a certain combination of roles they will then gain the
    Registered role and become a "registered" member unlocking the ability to see other channels.

    They will be prompted with helpful instructions to guide them from being
    not registered to fully registered.

    Registration does not apply to bots.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Sends an embedded message in the welcome channel with the new member's
        profile picture and a welcome message on join.

        DMs the user a welcome message and some hepful steps of how to register.

        Parameters
        ----------
        member : `discord.Member`
            The Discord Member which joined the guild.
        """

        if member.bot:
            return

        guild: discord.Guild = member.guild
        NOT_REGISTERED_CHANNEL: discord.TextChannel = self.client.get_channel(
            NOT_REGISTERED_CHANNEL_ID
        )
        ROLES_CHANNEL: discord.TextChannel = self.client.get_channel(ROLES_CHANNEL_ID)
        WELCOME_CHANNEL: discord.TextChannel = self.client.get_channel(
            WELCOME_CHANNEL_ID
        )
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        HUSKY_BOT: discord.Member = guild.get_member(self.client.user.id)
        SERVER_OWNER: discord.Member = guild.owner
        ADMIN_ROLE: discord.Role = discord.utils.get(guild.roles, name="Admin")

        co_admin_names: List[str] = [
            m.name for m in ADMIN_ROLE.members if m != SERVER_OWNER
        ]
        if len(co_admin_names) == 0:
            co_admin_names_fmt = ""
        elif len(co_admin_names) == 1:
            co_admin_names_fmt = f"__Co-Admin__: {co_admin_names[0]}"
        else:
            co_admin_names_fmt = "__Co-Admins__: {} & {}".format(
                ", ".join(co_admin_names[:-1]), co_admin_names[-1]
            )

        welcome_msg: discord.Embed = discord.Embed(
            description=f"Hey {member.mention} ({member.name}), welcome to **{guild}** 🎉! "
            f"Check your DMs from {HUSKY_BOT.mention} for further instructions!",
            color=discord.Color.red(),
        )
        welcome_msg.set_thumbnail(url=f"{member.display_avatar.url}")
        await WELCOME_CHANNEL.send(embed=welcome_msg)

        join_msg = (
            f"Welcome to the **{guild}** server {member.mention}!\n\n"
            "There **__are more than the 4 channels__** you currently see! "
            "Follow the registration steps in order to see the rest:\n"
            f":one: Select your year by reacting with an emoji under the Year section in {ROLES_CHANNEL.mention}.\n"
            f":two: Select a college/school of study by reacting with an emoji under the College/School section in {ROLES_CHANNEL.mention}.\n"
            "*Note: If you are unaffiliated with Northeastern, you can skip step 2 and pick Guest for step 1*\n\n"
            "If you have questions or need help getting registered feel free to DM "
            f"the Admins/Moderators or check out the {NOT_REGISTERED_CHANNEL.mention} channel.\n"
            f"Once you are fully registered you can pick courses in {COURSE_REGISTRATION_CHANNEL.mention}.\n"
            "**We hope that with student collaboration university will be easy and fun!**\n"
            f"__Server Owner__: {SERVER_OWNER.name} {co_admin_names_fmt}\n\n"
        )
        try:
            await member.send(join_msg)
        except discord.Forbidden:
            await NOT_REGISTERED_CHANNEL.send(join_msg)

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        """Adds Registered Role to fully registered members or removes it from unregistered ones.

        Parameters
        -----------
        before: `discord.Member`
            The member object before the update.
        after: `discord.Member`
            The member object after the update.
        """

        if after.bot:
            return

        if before.roles != after.roles:
            POSSIBLE_YEARS = {
                "Freshman",
                "Sophomore",
                "Middler",
                "Junior",
                "Senior",
                "Grad Student",
                "Alumni",
            }
            POSSIBLE_SCHOOLS = {
                "CCIS",
                "COE",
                "BCHS",
                "CAMD",
                "DMSB",
                "COS",
                "CSSH",
                "EXPLORE",
                "NUSL",
                "CPS",
            }
            SPECIAL_ROLES = {"NUly Admitted", "Guest"}

            guild: discord.Guild = after.guild
            REGISTERED_ROLE: discord.Role = discord.utils.get(
                guild.roles, name="Registered"
            )
            COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(
                COURSE_REGISTRATION_CHANNEL_ID
            )
            ROLES_CHANNEL: discord.TextChannel = self.client.get_channel(
                ROLES_CHANNEL_ID
            )

            has_year = has_school = is_special = False
            for role in after.roles:
                if role.name in POSSIBLE_YEARS:
                    has_year = True
                elif role.name in POSSIBLE_SCHOOLS:
                    has_school = True
                elif role.name in SPECIAL_ROLES:
                    is_special = True

            # They need both a year and school selected to be registered.
            # Having a special role overrides this requirement.
            if (has_year and has_school) or is_special:
                # Only send this message if the user doesn't currently have the Registered role.
                # This avoids sending the message to anyone who was already Registered.
                # If they just became Registered then, the message was already sent.
                if REGISTERED_ROLE not in after.roles:
                    try:
                        await after.send(
                            "Thank you for registering. You can now see all of the main channels."
                            f"You can pick courses in {COURSE_REGISTRATION_CHANNEL.mention} for access to course-specific chats!"
                        )
                    except discord.Forbidden:
                        pass

                # Add the role after the message is sent to avoid race conditions
                await after.add_roles(REGISTERED_ROLE)
            else:
                msg: Optional[str] = None
                if REGISTERED_ROLE not in after.roles:
                    if not has_year:
                        msg = (
                            "You still need to complete step 1 to register:\n"
                            f":one: Select your year by reacting with an emoji under the Year section in {ROLES_CHANNEL.mention}."
                        )
                    elif not has_school:
                        msg = (
                            "You still need to complete step 2 to register:\n"
                            f":two: Select a college/school of study by reacting with an emoji under the College/School section in {ROLES_CHANNEL.mention}."
                        )

                await after.remove_roles(REGISTERED_ROLE)
                if msg:
                    try:
                        await after.send(msg)
                    except discord.Forbidden:
                        NOT_REGISTERED_CHANNEL: discord.TextChannel = (
                            self.client.get_channel(NOT_REGISTERED_CHANNEL_ID)
                        )
                        await NOT_REGISTERED_CHANNEL.send(f"{after.mention}\n" + msg)


async def setup(client: commands.Bot):
    await client.add_cog(Onboarding(client))
