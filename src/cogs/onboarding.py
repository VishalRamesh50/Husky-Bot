import discord
from discord.ext import commands

from data.ids import (
    NOT_REGISTERED_ROLE_ID,
    NOT_REGISTERED_CHANNEL_ID,
    WELCOME_CHANNEL_ID,
    V_MONEY_ID,
    SUPERSECSEE_ID,
    SHWIN_ID,
    RULES_CHANNEL_ID,
    COURSE_REGISTRATION_CHANNEL_ID,
)


class Onboarding(commands.Cog):
    """Handles the onboarding experience for new members who join.

    When joining, every member is given the Not Registered Role.
    After a member has gained a certain combination of roles they will then lose the
    Not Registered role and become a "registered" member given unlocking the ability
    to see other channels.

    They will be prompted with helpful instructions to guide them from the Not Registered
    route to being a fully registered member.
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
        guild: discord.Guild = member.guild
        NOT_REGISTERED_ROLE: discord.Role = guild.get_role(NOT_REGISTERED_ROLE_ID)
        NOT_REGISTERED_CHANNEL: discord.TextChannel = guild.get_channel(
            NOT_REGISTERED_CHANNEL_ID
        )
        RULES_CHANNEL: discord.TextChannel = guild.get_channel(RULES_CHANNEL_ID)
        WELCOME_CHANNEL: discord.TextChannel = guild.get_channel(WELCOME_CHANNEL_ID)
        COURSE_REGISTRATION_CHANNEL: discord.TextChannel = guild.get_channel(
            COURSE_REGISTRATION_CHANNEL_ID
        )
        HUSKY_BOT: discord.Member = guild.get_member(self.client.user.id)
        V_MONEY: discord.Member = guild.get_member(V_MONEY_ID)
        SUPERSECSEE: discord.Member = guild.get_member(SUPERSECSEE_ID)
        SHWIN: discord.Member = guild.get_member(SHWIN_ID)

        # give new member Not Registered Role on join
        await member.add_roles(NOT_REGISTERED_ROLE)

        # send embedded message in WELCOME channel
        welcome_msg: discord.Embed = discord.Embed(
            description=f"Hey {member.mention} ({member.name}), welcome to **{guild}** 🎉! "
            f"Check your DMs from {HUSKY_BOT.mention} for further instructions!",
            colour=discord.Colour.red(),
        )
        welcome_msg.set_thumbnail(url=f"{member.avatar_url}")
        await WELCOME_CHANNEL.send(embed=welcome_msg)

        # send DM to user
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
            f"__Server Owner__: {V_MONEY.name} __Co-Admins__: {SUPERSECSEE.name} & {SHWIN.name}\n"
            "**We hope that with student collaboration university will be easy and fun!**\n\n"
            "If you need help using this bot just type `.help` in any channel!"
        )
        await member.send(join_msg)

    # Removes Not Registered Role from fully registered members or adds it to unregistered ones
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # if roles have changed
        if before.roles != after.roles and len(before.roles) != len(after.roles):
            # ================= CONSTANTS =========================
            POSSIBLE_YEARS = {'Freshman', 'Sophomore', 'Middler', 'Junior', 'Senior', 'Graduate', 'Alumni'}
            POSSIBLE_SCHOOLS = {'EXPLORE', 'COE', 'CCIS', 'CAMD', 'DMSB', 'BCHS', 'CPS', 'CSSH', 'COS', 'NUSL'}
            STUDENT = {'Student'}
            SPECIAL_ROLES = {'Newly Admitted', 'Guest'}

            NOT_REGISTERED_ROLE: discord.Role = discord.utils.get(after.guild.roles, name="Not Registered")
            COURSE_REGISTRATION_CHANNEL: discord.TextChannel = self.client.get_channel(COURSE_REGISTRATION_CHANNEL_ID)
            # ================= VARIABLES ==========================
            has_year = has_school = is_student = is_special = False

            # iterate through members roles
            for role in after.roles:
                # if member's role is a Year
                if role.name in POSSIBLE_YEARS:
                    has_year = True
                # if member's role is a School
                elif role.name in POSSIBLE_SCHOOLS:
                    has_school = True
                # if member's role is Student
                elif role.name in STUDENT:
                    is_student = True
                # if member's role is special
                elif role.name in SPECIAL_ROLES:
                    is_special = True

            # if the user is a bot or is has a combination of Student, Years, and Schools or Student and Special Roles
            if after.bot or (is_student and ((has_year and has_school) or is_special)):
                # only send this message when the user was previously unregistered and now don't have the not registered role
                if NOT_REGISTERED_ROLE in before.roles and NOT_REGISTERED_ROLE not in after.roles:
                    await after.send("Thank you for registering. You can now see all of the main channels."
                                     f"You can pick courses in {COURSE_REGISTRATION_CHANNEL.mention} for access to course-specific chats!")

                # remove the NOT_REGISTERED_ROLE
                await after.remove_roles(NOT_REGISTERED_ROLE)
            else:
                RULES_CHANNEL: discord.TextChannel = self.client.get_channel(RULES_CHANNEL_ID)
                # if the member did not just join and is NOT REGISTERED role has been given
                if len(before.roles) != 1 and NOT_REGISTERED_ROLE in after.roles:
                    # ensure that only one step is being sent at a time
                    if not is_student:
                        await after.send('You still need to complete step 1:\n'
                                         f':one: Accept the rules by reacting with a :thumbsup: in {RULES_CHANNEL.mention} to become a Student.')
                    elif not is_special:
                        if not has_year:
                            await after.send('You still need to complete step 2:\n'
                                             f':two: Select your year by reacting with a number in {RULES_CHANNEL.mention}.')
                        elif not has_school:
                            await after.send('You still need to complete step 3:\n'
                                             f':three: Assign yourself a school/major and courses in {COURSE_REGISTRATION_CHANNEL.mention} '
                                             'right here: <https://discordapp.com/channels/485196500830519296/485279507582943262/485287996833267734>.')

                # add the NOT_REGISTERED_ROLE
                await after.add_roles(NOT_REGISTERED_ROLE)


def setup(client):
    client.add_cog(Onboarding(client))
