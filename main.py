import discord
from discord.ext import commands
import asyncio
from itertools import cycle
from creds import TOKEN

EXTENSIONS = ['voice']

client = commands.Bot(command_prefix='.')  # bot prefix
client.remove_command('help')  # remove default help command
STATUS = ['With Huskies!', '.help']  # bot statuses


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


@client.command(pass_context=True)  # help command
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        description='Here are the commands for Husky Bot! The prefix is `.`',
        colour=discord.Colour.red()
    )

    embed.set_author(name='Help', icon_url='https://i.imgur.com/PKev2zr.png')
    embed.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png')
    embed.add_field(name='.ping', value='Returns Pong!', inline=False)  # ping documentation
    embed.add_field(name='.echo', value='Repeats anything typed after the command!', inline=False)  # echo documentation
    embed.add_field(name='.reminder', value="""Reminds you anything in any amount of time!
    Follow this format `.remind [Reminder] in [Number] [Unit of Time]`""", inline=False)  # timer documentation
    embed.add_field(name='.clear', value='Deletes a certain amount of messages! Must be more than 1!', inline=False)  # clear documentation
    embed.add_field(name='.join', value='Joins voice channel. You must be in a voice channel to use.', inline=False)  # join documentation
    embed.add_field(name='.play', value='Plays any music by searching on YouTube!', inline=False)  # play documentation
    embed.add_field(name='.pause', value='Pauses music!', inline=False)  # pause documentation
    embed.add_field(name='.resume', value='Resumes music!', inline=False)  # resume documentation
    embed.add_field(name='.skip', value='Skips music!', inline=False)  # skip documentation
    embed.add_field(name='.queue', value='Adds music to queue!', inline=False)  # queue documentation
    embed.add_field(name='.leave', value='Leaves voice channel! Must be in one in the first place', inline=False)  # leave documentation

    await client.delete_message(ctx.message)  # deleted user's command
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
async def clear(ctx, amount=1):
    channel = ctx.message.channel
    messages = []
    async for message in client.logs_from(channel, limit=int(amount)+1):
        messages.append(message)
    await client.delete_messages(messages)
    await client.say('Messages deleted.')


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
    await client.send_message(client.get_channel('485469821417422850'), embed=embed)


@client.event  # displays before & after state of edited message
async def on_message_edit(message1, message2):
    author = message1.author
    before_content = message1.content
    channel = message1.channel
    after_content = message2.content
    dyno_action_log_channel_id = '485469821417422850'
    embed = discord.Embed(
        description=f'**Message edited in {channel.mention}**',
        colour=discord.Colour.red()
    )

    embed.set_author(name=author, icon_url=author.avatar_url)
    embed.add_field(name='Before', value=before_content, inline=False)
    embed.add_field(name='After', value=after_content, inline=False)
    embed.set_footer(text=f'User ID: {author.id}')
    await client.send_message(client.get_channel(dyno_action_log_channel_id), embed=embed)


'''
async def not_registered_reminder():  # sends announcement to register 2 times a week
    await client.wait_until_ready()
    not_registered_role = '501184186498154511'
    rules_channel_id = '485279439593144362'
    course_registration_channel_id = '485279507582943262'
    not_registered_channel_id = '501193530325205003'
    test_channel_id = '485217538893021185'
    reminder = f":pushpin: <@&{not_registered_role}> you either haven't registered to become a Student, chosen your year, or declared a major yet!\n" \
               f":one: Head over to {client.get_channel(rules_channel_id).mention} , read and accept by reacting with a :thumbsup: and choose your year.\n" \
               f":two: Next, head over to {client.get_channel(course_registration_channel_id).mention} and choose your major and courses now!\n" \
               f":three: Finally, type `?choose Not Registered` in {client.get_channel(not_registered_channel_id).mention} . You now are an official member!"

    while not client.is_closed:
        await client.send_message(client.get_channel(test_channel_id), reminder)
        await asyncio.sleep(302,400)  # 2 times a week
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
    if valid_unit:
        try:
            await asyncio.sleep(int(time))
            await client.send_message(author, reminder)
        except ValueError:  # if time is not a number
            await client.say('You have to use a number for the second to last term.')
    else:  # if not a valid unit of time
        await client.say('Your unit of measurement must be a second, minute, hour, day, or week.')


@client.command()  # stops bot
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
'client.loop.create_task(not_registered_reminder())  # reminder for not-registered channel'
client.run(TOKEN)  # run bot
