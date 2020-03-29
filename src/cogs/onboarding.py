import discord
from discord.ext import commands
from typing import List

from checks import is_admin
from data.ids import (
    COURSE_REGISTRATION_CHANNEL_ID,
    NOT_REGISTERED_CHANNEL_ID,
    RULES_CHANNEL_ID,
    WELCOME_CHANNEL_ID,
)


class Onboarding(commands.Cog):
    """Handles the onboarding experience for new members who join.

    When joining, every member is given the Not Registered Role.
    After a member has gained a certain combination of roles they will then lose the
    Not Registered role and become a "registered" member given unlocking the ability
    to see other channels.

    They will be prompted with helpful instructions to guide them from the Not Registered
    route to being a fully registered member.

    Registration does not apply to bots.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @is_admin()
    @commands.command()
    async def test(self, ctx, member: discord.Member) -> None:
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
        NOT_REGISTERED_ROLE: discord.Role = discord.utils.get(
            guild.roles, name="Not Registered"
        )
        NOT_REGISTERED_CHANNEL: discord.TextChannel = self.client.get_channel(
            NOT_REGISTERED_CHANNEL_ID
        )
        RULES_CHANNEL: discord.TextChannel = self.client.get_channel(RULES_CHANNEL_ID)
        WELCOME_CHANNEL: discord.TextChannel = self.client.get_channel(
            WELCOME_CHANNEL_ID
        )
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        HUSKY_BOT: discord.Member = guild.get_member(self.client.user.id)
        SERVER_OWNER: discord.Member = guild.owner
        ADMIN_ROLE: discord.Role = discord.utils.get(guild.roles, name="Admin")
        admins = filter(
            lambda m: ADMIN_ROLE in m.roles and m != SERVER_OWNER, guild.members
        )
        admin_names: List[str] = [a.name for a in admins]
        if len(admin_names) > 2:
            fmt = "{}, & {}".format(", ".join(admin_names[:-1]), admin_names[-1])
        else:
            fmt = " & ".join(admin_names)
        co_admin_msg = f"__Co-Admins__: {fmt}"

        await member.add_roles(NOT_REGISTERED_ROLE)

        welcome_msg: discord.Embed = discord.Embed(
            description=f"Hey {member.mention} ({member.name}), welcome to **{guild}** 🎉! "
            f"Check your DMs from {HUSKY_BOT.mention} for further instructions!",
            colour=discord.Colour.red(),
        )
        welcome_msg.set_thumbnail(url=f"{member.avatar_url}")
        await WELCOME_CHANNEL.send(embed=welcome_msg)

        join_msg = (
            f"Welcome to the **{guild}** server {member.mention}!\n"
            "There **__are more than the 3 channels__** you currently see! "
            "Follow the registration steps in order to see the rest.\n\n"
            f":one: Accept the rules by reacting with a 👍 in {RULES_CHANNEL.mention} to become a Student.\n"
            f":two: Select your year by reacting with a number in {RULES_CHANNEL.mention}.\n"
            f":three: Assign yourself a school/major and courses in {COURSE_REGISTRATION_CHANNEL.mention} right here: "
            "<https://discordapp.com/channels/485196500830519296/485279507582943262/485287996833267734>.\n"
            "*Note: If you are not affiliated with Northeastern, you can skip step 3 and pick Guest for step 2*\n\n"
            "If you have questions or need help getting registered feel free to DM "
            f"the Admins/Moderators or check out the {NOT_REGISTERED_CHANNEL.mention} channel.\n"
            f"__Server Owner__: {SERVER_OWNER.name} __Co-Admins__: {co_admin_msg}\n"
            "**We hope that with student collaboration university will be easy and fun!**\n\n"
            "If you need help using this bot just type `.help` in any channel!"
        )
        await member.send(join_msg)

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        """Removes Not Registered Role from fully registered members or adds it to unregistered ones.

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
            STUDENT = {"Student"}
            SPECIAL_ROLES = {"Newly Admitted", "Guest"}

            guild: discord.Guild = after.guild
            NOT_REGISTERED_ROLE: discord.Role = discord.utils.get(
                guild.roles, name="Not Registered"
            )
            COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(
                COURSE_REGISTRATION_CHANNEL_ID
            )
            RULES_CHANNEL: discord.TextChannel = self.client.get_channel(
                RULES_CHANNEL_ID
            )

            has_year = has_school = is_student = is_special = False
            for role in after.roles:
                if role.name in POSSIBLE_YEARS:
                    has_year = True
                elif role.name in POSSIBLE_SCHOOLS:
                    has_school = True
                elif role.name in STUDENT:
                    is_student = True
                elif role.name in SPECIAL_ROLES:
                    is_special = True

            # The Student role is mandatory.
            # If they also have a special role then they are registered.
            # Otherwise, they will need both a year and a school.
            if is_student and ((has_year and has_school) or is_special):
                # Only send this message if the user was previously unregistered to avoid
                # triggering registration messages when updating any roles.
                if (
                    NOT_REGISTERED_ROLE in before.roles
                    and NOT_REGISTERED_ROLE not in after.roles
                ):
                    await after.send(
                        "Thank you for registering. You can now see all of the main channels."
                        f"You can pick courses in {COURSE_REGISTRATION_CHANNEL.mention} for access to course-specific chats!"
                    )

                await after.remove_roles(NOT_REGISTERED_ROLE)
            else:
                # if the member did not just join and is NOT REGISTERED role has been given
                if len(before.roles) != 1 and NOT_REGISTERED_ROLE in after.roles:
                    if not is_student:
                        await after.send(
                            "You still need to complete step 1:\n"
                            f":one: Accept the rules by reacting with a 👍 in {RULES_CHANNEL.mention} to become a Student."
                        )
                    elif not has_year:
                        await after.send(
                            "You still need to complete step 2:\n"
                            f":two: Select your year by reacting with a number in {RULES_CHANNEL.mention}."
                        )
                    elif not has_school:
                        await after.send(
                            "You still need to complete step 3:\n"
                            f":three: Assign yourself a school/major and courses in {COURSE_REGISTRATION_CHANNEL.mention} "
                            "right here: <https://discordapp.com/channels/485196500830519296/485279507582943262/485287996833267734>."
                        )

                await after.add_roles(NOT_REGISTERED_ROLE)


def setup(client: commands.Bot):
    client.add_cog(Onboarding(client))
