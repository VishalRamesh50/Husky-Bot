import discord
from discord.ext import commands
import asyncio
from itertools import cycle
from time import strftime
import time
import random
import NUDiningHours
import os
if os.path.isfile("creds.py"):
    from creds import TOKEN  # local TOKEN
else:
    TOKEN = os.environ["TOKEN"]  # TOKEN from Heroku

EXTENSIONS = ['voice']

client = commands.Bot(command_prefix='.')  # bot prefix
client.remove_command('help')  # remove default help command
STATUS = ['With Huskies!', '.help']  # bot statuses

# SERVER SPECIFIC ID'S
DYNO_BOT_ID = '155149108183695360'
COURSE_REGISTRATION_CHANNEL_ID = '485279507582943262'
ADMIN_ID = '485227611375534143'
DYNO_ACTION_LOG_CHANNEL_ID = '485469821417422850'
NOT_REGISTERED_ID = '501184186498154511'
RULES_CHANNEL_ID = '485279439593144362'
COURSE_REGISTRATION_CHANNEL_ID = '485279507582943262'
NOT_REGISTERED_CHANNEL_ID = '501193530325205003'
TEST_CHANNEL_ID = '485217538893021185'


@client.event  # Bot is Ready to Go
async def on_ready():
    print(f"{client.user.name} is ONLINE!")


async def change_status():
    await client.wait_until_ready()
    msgs = cycle(STATUS)

    while not client.is_closed:
        current_status = next(msgs)
        await client.change_presence(game=discord.Game(name=current_status))  # display status
        await asyncio.sleep(5)  # change status every 5 seconds


@client.event  # error handler
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.CheckFailure):  # if command was not used with required role
        await client.send_message(channel, 'Insufficient Role')


@client.event  # AutoDelete Dyno Bot's Messages in #course-registration
async def on_message(message):
    if message.author.id == DYNO_BOT_ID and message.channel.id == COURSE_REGISTRATION_CHANNEL_ID:
        await asyncio.sleep(5)
        await client.delete_message(message)
    await client.process_commands(message)


@client.event  # member leave message
async def on_member_remove(member):
    await client.send_message(member, "We are *really* sad to see you go. If we haven't met your expectations we would really love for you to fill out this form to give us feedback. There's only 2 questions. Thank you! https://goo.gl/forms/9a0F9RoIIPm2CYnw2")


@client.command(pass_context=True)  # help command
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        description='Here are the commands for Husky Bot! The prefix is `.`',
        colour=discord.Colour.red()
    )
    embed.set_author(name='Help', icon_url='https://i.imgur.com/PKev2zr.png')
    embed.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
    if ADMIN_ID in [role.id for role in author.roles]:
        embed.add_field(name='.clear', value='Deletes a certain amount of messages! Must be more than 1!', inline=False)  # clear documentation
        embed.add_field(name='.logout', value='Bot logs out!', inline=False)  # logout documentation
    embed.add_field(name='.ping', value='Returns Pong!', inline=False)  # ping documentation
    embed.add_field(name='.echo', value='Repeats anything typed after the command!', inline=False)  # echo documentation
    embed.add_field(name='.flip', value='Flips a coin!', inline=False)  # flip documentation
    embed.add_field(name='.menu', value='Generates link to NU Dining menu!', inline=False)  # menu documentation
    embed.add_field(name='.hours', value='Tells whether a chosen dining hall is open or not!', inline=False)  # hours documentation
    embed.add_field(name='.reminder', value="Reminds you anything in any amount of time! Follow this format: `.remind [Reminder] in [Number] [Unit of Time]`", inline=False)  # timer documentation
    embed.add_field(name='.invite', value='Generates server invite link!', inline=False)  # invite documentation
    embed.add_field(name='.join', value='Joins voice channel. You must be in a voice channel to use.', inline=False)  # join documentation
    embed.add_field(name='.play', value='Plays any music by searching on YouTube!', inline=False)  # play documentation
    embed.add_field(name='.pause', value='Pauses music!', inline=False)  # pause documentation
    embed.add_field(name='.resume', value='Resumes music!', inline=False)  # resume documentation
    embed.add_field(name='.skip', value='Skips music!', inline=False)  # skip documentation
    embed.add_field(name='.queue', value='Adds music to queue!', inline=False)  # queue documentation
    embed.add_field(name='.display_queue', value='Displays current queue!', inline=False)  # display_queue documentation
    embed.add_field(name='.leave', value='Leaves voice channel! Must be in one in the first place', inline=False)  # leave documentation

    await client.delete_message(ctx.message)  # deletes user's command
    await client.say('Check your DM!')
    await client.send_message(author, embed=embed)  # sends user a DM


@client.command()  # replies Pong! given .ping
async def ping():
    await client.say('Pong!')


@client.command()  # repeats given statement after .echo
async def echo(*args):
    output = ''
    for word in args:
        output += word
        output += ' '
    await client.say(output)


@client.command(pass_context=True)  # deletes set amount of messages
@commands.has_role('Admin')
async def clear(ctx, amount=''):
    channel = ctx.message.channel
    messages = []
    await client.say(f"Amount is {amount}")
    if amount == '0':
        await client.say("Cannot delete 0 messages.")
    try:
        async for message in client.logs_from(channel, limit=int(amount)+1):
            messages.append(message)
        await client.delete_messages(messages)
        await client.say(f"{len(messages)-1} messages deleted.")
    except ValueError:
        await client.say("Must use a number.")


'''
@client.event  # says what message was deleted and by whom
async def on_message_delete(message):
    author = message.author
    content = message.content
    channel = message.channel
    embed = discord.Embed(
        description=f'**Message sent by {author.mention} deleted in {channel.mention}**\n {content}',
        colour=discord.Colour.red()
    )

    embed.set_author(name=author, icon_url=author.avatar_url)
    embed.set_footer(text=f'ID: {message.id}')
    await client.send_message(client.get_channel(DYNO_ACTION_LOG_CHANNEL_ID), embed=embed)


@client.event  # displays before & after state of edited message
async def on_message_edit(message1, message2):
    author = message1.author
    before_content = message1.content
    channel = message1.channel
    after_content = message2.content
    try:
        embed = discord.Embed(
            description=f'**Message edited in {channel.mention}**',
            colour=discord.Colour.red()
        )

        embed.set_author(name=author, icon_url=author.avatar_url)
        embed.add_field(name='Before', value=before_content, inline=False)
        embed.add_field(name='After', value=after_content, inline=False)
        embed.set_footer(text=f'User ID: {author.id}')
        await client.send_message(client.get_channel(DYNO_ACTION_LOG_CHANNEL_ID), embed=embed)
    except AttributeError:
        print("'PrivateChannel' object has no attribite 'mention'")
    except discord.errors.HTTPException:
        print("HTTPException")


async def not_registered_reminder():  # sends announcement to register 2 times a week
    await client.wait_until_ready()
    reminder = (f":pushpin: <@&{NOT_REGISTERED_ID}> you either haven't registered to become a Student, chosen your year, or declared a major yet!\n"
                f":one: Head over to {client.get_channel(RULES_CHANNEL_ID).mention} , read and accept by reacting with a :thumbsup: and choose your year.\n"
                f":two: Next, head over to {client.get_channel(COURSE_REGISTRATION_CHANNEL_ID).mention} and choose your major and courses now!\n"
                f":three: Finally, type `?choose Not Registered` in {client.get_channel(NOT_REGISTERED_CHANNEL_ID).mention} . You now are an official member!")

    while not client.is_closed:
        await client.send_message(client.get_channel(TEST_CHANNEL_ID), reminder)
        await asyncio.sleep(302400)  # 2 times a week
'''


@client.command(pass_context=True)  # reminder
async def reminder(ctx, *args):
    author = ctx.message.author
    reminder = ''
    time = args[len(args)-2]  # second to last term -> time as a string
    SECOND_POSSIBILITIES = ('sec', 'secs', 'second', 'seconds', 's')
    MINUTE_POSSIBILITIES = ('min', 'mins', 'minute', 'minutes', 'm')
    HOUR_POSSIBILITIES = ('hr', 'hrs', 'hour', 'hours', 'h')
    DAY_POSSIBILITIES = ('day', 'days', 'd')
    WEEK_POSSIBILITIES = ('week', 'weeks', 'w')
    valid_unit = True
    if args[-1].lower() in SECOND_POSSIBILITIES:
        time = time
    elif args[-1].lower() in MINUTE_POSSIBILITIES:
        time *= 60
    elif args[-1].lower() in HOUR_POSSIBILITIES:
        time *= 3600
    elif args[-1].lower() in DAY_POSSIBILITIES:
        time *= 86400
    elif args[-1].lower() in WEEK_POSSIBILITIES:
        time *= 604800
    else:
        valid_unit = False
    for word in args:
        if word == 'in':
            break
        else:
            reminder += word
            reminder += ' '
    if "in" != args[len(args)-3]:
        await client.say(f"You must include the word `in` between your reminder and the time.\n"
                         f"Incorrect: `.reminder Husky Bot is cool 5 secs`\n"
                         f"Correct: `.reminder Husky Bot is cool in 5 secs`")
    else:
        if valid_unit:
            try:
                await asyncio.sleep(int(time))
                await client.say(f"I will remind you about `{reminder}` in `{time} seconds`")
                await client.send_message(author, f"Here is your reminder for `{reminder}`")
            except ValueError:  # if time is not a number
                await client.say(f"You have to use a number for the 2nd to last term.\n"
                                 f"Incorrect: `.reminder Husky Bot is cool in five secs`\n"
                                 f"Correct: `.reminder Husky Bot is cool in 5 secs`")
        else:  # if not a valid unit of time
            await client.say(f"Your unit of measurement must be a second, minute, hour, day, or week.\n"
                             f"Incorrect: `.reminder Husky Bot is cool in 1 month`\n"
                             f"Correct: `.reminder Husky Bot is cool in 4 weeks`")


@client.command()  # generates invite link to server
async def invite():
    await client.say('discord.gg/CP9MBRH')


@client.command()  # generates link to NU dining menu
async def menu():
    await client.say('https://new.dineoncampus.com/Northeastern/menus')


@client.command(pass_context=True)
async def hours(ctx, content):
    content = content.upper()
    location = ''
    day = strftime("%A", time.localtime())
    hour = int(strftime("%H", time.localtime()))
    minute = int(strftime("%M", time.localtime()))
    valid_location = True
    if content == "IV":
        location = NUDiningHours.IV
    elif content == "STWEST":
        location = NUDiningHours.STWEST
    elif content == "STEAST":
        location = NUDiningHours.STEAST
    elif content == "OUTTAKES":
        location = NUDiningHours.OUTTAKES
    elif content == "REBECCAS" or content == "REBECCA'S":
        if day[0] == 'S':
            day = 'Weekend'
        else:
            day = 'Weekday'
        location = NUDiningHours.REBECCAS
    elif content == "UBURGER":
        if day != 'Saturday' or day != 'Sunday':
            day = 'Weekday'
        location = NUDiningHours.UBURGER
    elif content == "KIGO":
        if day[0] == 'S':
            day = 'Weekend'
        location = NUDiningHours.KIGO
    elif content == "STARBUCKS":
        if day != 'Saturday' or day != 'Sunday':
            day = 'Weekday'
        location = NUDiningHours.STARBUCKS
    elif content == "SUBWAY":
        if day[0] == 'S':
            day = 'Weekend'
        location = NUDiningHours.SUBWAY
    elif content == "POPEYES":
        if day != 'Saturday' or day != 'Sunday':
            day = 'Weekday'
        location = NUDiningHours.POPEYES
    else:
        valid_location = False
    if valid_location:
        if location[day] == "Closed":
            await client.say(f"{content} is CLOSED today.")
        else:
            opening_hour = location[day][0] % 12
            if opening_hour == 0:
                opening_hour = 12
            opening_minute = location[day][1]
            opening_period = location[day][2]
            closing_hour = location[day][3] % 12
            if closing_hour == 0:
                closing_hour = 12
            closing_minute = location[day][4]
            closing_period = location[day][5]
            hours_of_operation = f"It's open from {opening_hour}:{opening_minute} {opening_period} - {closing_hour}:{closing_minute} {closing_period} today."
            if hour >= opening_hour and hour <= closing_hour:
                if minute >= int(opening_minute) and hour < int(closing_minute):
                    await client.say(f"{content} is OPEN now! {hours_of_operation}")
                else:
                    await client.say(f"{content} is CLOSED now. {hours_of_operation}")
            else:
                await client.say(f"{content} is CLOSED now. {hours_of_operation}")
    else:
        await client.say("Error: Location options are: Stwest, Steast, IV, Outtakes, Rebecca's, UBurger, Kigo's Kitchen, Starbucks, Subway, Popeyes.")


@client.command()  # coin flip
async def flip():
    outcome = random.randint(0, 1)
    if outcome == 0:
        await client.say("Heads!")
    else:
        await client.say("Tails!")


@client.command()  # stops bot
@commands.has_role('Admin')
async def logout():
    await client.say("Alright I'll stop now.")
    print(f"{client.user.name} is logging out.")
    await client.logout()


if __name__ == '__main__':
    for extension in EXTENSIONS:
        try:
            client.load_extension(extension)
        except Exception as error:
            print('{} cannot be loaded. [{}]'.format(extension, error))
client.loop.create_task(change_status())  # iniate loop for status
# client.loop.create_task(not_registered_reminder())  # reminder for not-registered channel
client.run(TOKEN)  # run bot
