import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    # help command
    @commands.command()
    async def help(self, ctx, *args):
        author = ctx.author
        channel = ctx.channel
        message = ctx.message
        try:
            selection = args[0].upper()
        except IndexError:
            selection = 'HELP'
        # if user has administrator permissions
        admin = author.permissions_in(channel).administrator
        mod = discord.utils.get(author.roles, name='Moderator')
        await message.delete()  # deletes user's command
        questionMarkImageURL = 'https://cdn4.iconfinder.com/data/icons/colorful-design-basic-icons-1/550/question_doubt_red-512.png'
        huskyBotIconURL = self.client.user.avatar_url
        if selection == 'HELP':
            embed = discord.Embed(
                description=("To see a page, just add the page number after the `.help` command.\n"
                             "Like this: `.help 1`"),
                colour=discord.Colour.red()
            )
            embed.set_author(name='Help', icon_url=huskyBotIconURL)
            embed.set_thumbnail(url=questionMarkImageURL)
            if admin:
                embed.add_field(name='Page rr | Reaction Roles', value='To use reaction role commands!', inline=False)  # reaction roles page
                embed.add_field(name='Page cr | Course Registration', value='To use course registration commands!', inline=False)  # course registration page
                embed.add_field(name='Page ccs | Course Creation Shortcuts', value='To use course creation shotcut commands!', inline=False)  # course creation shorcuts page
            if mod:
                embed.add_field(name='Page stats | Stats', value="How to use Stats Commands!", inline=False)  # stats page
                embed.add_field(name='Page 0 | Clear', value="How to use Clear Command!", inline=False)  # clear page
            embed.add_field(name='Page 1 | Reminder', value='How to use Reminder Command!', inline=False)  # reminder page
            embed.add_field(name='Page 2 | Hours', value='How to use Hours Command!', inline=False)  # hours page
            embed.add_field(name='Page 3 | Open', value='How to use Open Command!', inline=False)  # open page
            embed.add_field(name='Page 4 | Ice Cream', value='How to use Ice Cream Command!', inline=False)  # ice-cream page
            embed.add_field(name='Page 5 | Day Date', value='How to use Day Date Command!', inline=False)  # day date page
            embed.add_field(name='Page 6 | Music', value='How to use Music Commands!', inline=False)  # music page
            embed.add_field(name='Page 7 | Miscellaneous', value="How to use Miscellaneous Commands!", inline=False)  # miscellaneous page
            embed.add_field(name='Page 8 | Choose', value="How to use the Choose Command!", inline=False)  # choose page
            embed.add_field(name='Page 9 | Whois', value="How to use the Whois Command!", inline=False)  # whois page
            embed.add_field(name='Page 10 | Playing', value="How to use the Playing Command!", inline=False)  # playing page
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=embed)  # sends user a DM
            return

        if admin and selection == 'RR':
            # reaction roles help page
            rr = discord.Embed(
                description="To see a page, just add the page name after the `.help` command.\n"
                            "Like this: `.help newrr`",
                colour=discord.Colour.red())
            rr.set_author(name='Help | Reaction Role Commands', icon_url=huskyBotIconURL)
            rr.set_thumbnail(url=questionMarkImageURL)
            rr.add_field(name='Commands', value='`.newrr`, `.fetchrr`, `.removerr`, `removeallrr`', inline=False)  # newrr documentation
            rr.add_field(name='Page newrr | Adding New Reaction Role', value='How to use the `.newrr` Command!', inline=False)  # newrr documentation
            rr.add_field(name='Page fetchrr | Fetching Reaction Role Information', value='How to use the `.fetchrr` Command!', inline=False)  # fetchrr documentation
            rr.add_field(name='Page removerr | Removing a Reaction Role', value='How to use the `.removerr` Command!', inline=False)  # removerr documentation
            rr.add_field(name='Page removeallrr | Removing All Reaction Roles for Message', value='How to use the `.removeallrr` Command!', inline=False)  # removeallrr documentation
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=rr)  # sends user a DM
            return
        if admin and selection == 'NEWRR':
            # newrr help page
            newrr = discord.Embed(colour=discord.Colour.red())
            newrr.set_author(name='Help | newrr', icon_url=huskyBotIconURL)
            newrr.set_thumbnail(url=questionMarkImageURL)
            newrr.add_field(name='Command', value='`.newrr [channel] [message_id] [reaction/emoji] [role]`', inline=False)
            newrr.add_field(name='Example', value='`.newrr #rules 123456789876543210 👍 @Student`', inline=False)
            newrr.add_field(name='Note', value=('Given **channel** can be in the form of a mentioned channel or just the name.\n'
                                                'Given **message id** must be a valid message id and a number.\n'
                                                'Given **emoji** must be a valid emoji in the correct form (Ex: :thumbs_up:).\n'
                                                'Given **role** can be in the form of a mentioned role or just the name.'), inline=False)
            newrr.add_field(name='Purpose', value='Allows for the user to select a specific message that users can react to with a chosen emoji to get assigned a role and unreact to remove the role.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=newrr)  # sends user a DM
            return
        if admin and selection == 'FETCHRR':
            # fetchrr help page
            fetchrr = discord.Embed(colour=discord.Colour.red())
            fetchrr.set_author(name='Help | fetchrr', icon_url=huskyBotIconURL)
            fetchrr.set_thumbnail(url=questionMarkImageURL)
            fetchrr.add_field(name='Command', value='`.fetchrr [message_id]`', inline=False)
            fetchrr.add_field(name='Example', value='`.fetchrr 123456789876543210`', inline=False)
            fetchrr.add_field(name='Note', value='Given message id must be a valid message id and a number.', inline=False)
            fetchrr.add_field(name='Purpose', value='Fetches all the keys, reaction, and roles corresponding to each reaction role for the given message id.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=fetchrr)  # sends user a DM
            return
        if admin and selection == 'REMOVERR':
            # removerr help page
            removerr = discord.Embed(colour=discord.Colour.red())
            removerr.set_author(name='Help | removerr', icon_url=huskyBotIconURL)
            removerr.set_thumbnail(url=questionMarkImageURL)
            removerr.add_field(name='Command', value='`.removerr [key]`', inline=False)
            removerr.add_field(name='Example', value='`.removerr F0xUOpxMv`', inline=False)
            removerr.add_field(name='Note', value='Given key must be a valid key. Each reaction role is assigned a unique key and can be found in the embedded message upon creation of the reaction role or by using the `.fetchrr` command.', inline=False)
            removerr.add_field(name='Purpose', value='Allows for the user to delete any reaction role by giving the unique key.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=removerr)  # sends user a DM
            return
        if admin and selection == 'REMOVEALLRR':
            # removeallrr help page
            removeallrr = discord.Embed(colour=discord.Colour.red())
            removeallrr.set_author(name='Help | removeallrr', icon_url=huskyBotIconURL)
            removeallrr.set_thumbnail(url=questionMarkImageURL)
            removeallrr.add_field(name='Command', value='`.removeallrr [message_id]`', inline=False)
            removeallrr.add_field(name='Example', value='`.removeallrr 123456789876543210`', inline=False)
            removeallrr.add_field(name='Note', value='Given message id must be a valid message id and a number.', inline=False)
            removeallrr.add_field(name='Purpose', value='Allows for the user to delete all reaction roles from a given message at once.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=removeallrr)  # sends user a DM
            return

        if admin and selection == 'CR':
            # course registration help page
            cr = discord.Embed(
                description="To see a page, just add the page name after the `.help` command.\n"
                            "Like this: `.help toggleAD`",
                colour=discord.Colour.red())
            cr.set_author(name='Help | Course Registration Commands', icon_url=huskyBotIconURL)
            cr.set_thumbnail(url=questionMarkImageURL)
            cr.add_field(name='Commands', value='`.toggleAD`, `.choose`, `.newSemester`, `.clearCourses`, `clearReactions`, `newEmbed`, `editEmbedImage`, `editEmbedTitle`, `editCourseContent`', inline=False)  # available commands
            cr.add_field(name='Page toggleAD | Toggling AutoDelete', value='How to use the `.toggleAD` Command!', inline=False)  # toggleAD documentation
            cr.add_field(name='Page choose | Toggle Courses', value='How to use the `.choose` Command!', inline=False)  # choose documentation
            cr.add_field(name='Page newSemester | New Semester', value='How to use the `.newSemester` Command!', inline=False)  # newSemester documentation
            cr.add_field(name='Page clearCourses | Clear Courses', value='How to use the `.clearCourses` Command!', inline=False)  # clearCourses documentation
            cr.add_field(name='Page clearReactions | Clear Reactions', value='How to use the `.clearReactions` Command!', inline=False)  # clearReactions documentation
            cr.add_field(name='Page newEmbed | New Course Reaction Embed Message', value='How to use the `.newEmbed` Command!', inline=False)  # newEmbed documentation
            cr.add_field(name='Page editEmbedImage | Edit Embedded Message Image', value='How to use the `.editEmbedImage` Command!', inline=False)  # editEmbedImage documentation
            cr.add_field(name='Page editEmbedTitle | Edit Embedded Message Title', value='How to use the `.editEmbedTitle` Command!', inline=False)  # editEmbedTitle documentation
            cr.add_field(name='Page editCourseContent | Edit Course Content', value='How to use the `.editCourseContent` Command!', inline=False)  # editCourseContent documentation
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=cr)  # sends user a DM
            return
        if admin and selection == 'TOGGLEAD':
            # toggleAD help page
            toggleAD = discord.Embed(colour=discord.Colour.red())
            toggleAD.set_author(name='Help | toggleAD', icon_url=huskyBotIconURL)
            toggleAD.set_thumbnail(url=questionMarkImageURL)
            toggleAD.add_field(name='Command', value='`.toggleAD`', inline=False)
            toggleAD.add_field(name='Example', value='`.toggleAD`', inline=False)
            toggleAD.add_field(name='Permissions', value='Administrator', inline=False)
            toggleAD.add_field(name='Note', value="Will toggle the auto-delete functionality of the course registration, switching from deleting Husky Bot's messages to not.", inline=False)
            toggleAD.add_field(name='Purpose', value='Allows for user to toggle off auto-delete when creating new messages via HuskyBot in `#course-registration` and then toggle it back on to avoid spam from other users.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=toggleAD)  # sends user a DM
            return
        if selection == 'CHOOSE' or selection == '8':
            # choose help page
            choose = discord.Embed(colour=discord.Colour.red())
            choose.set_author(name='Help | choose', icon_url=huskyBotIconURL)
            choose.set_thumbnail(url=questionMarkImageURL)
            choose.add_field(name='Command', value='`.choose [role-name]`', inline=False)
            choose.add_field(name='Example', value='`.choose [CS-2500]` or `.choose [cs 2500]` or `.choose spring green`', inline=False)
            choose.add_field(name='Permissions', value='Administrator & Everyone', inline=False)
            choose.add_field(name='Note', value=("Non-admin users can only use this command in `#course-registration`.\n"
                                                 "Non-admin users can only toggle courses in `#course-registration`.\n"
                                                 "Admins can toggle any role and do it anywhere.\n"
                                                 "Role names are case-insensitive, spaces are allowed, and courses do not require a '-' even though it is in the name."), inline=False)
            choose.add_field(name='Purpose', value='Toggle #course-registration roles without having to search for their reactions in the large channel.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=choose)  # sends user a DM
            return
        if admin and selection == 'NEWSEMESTER':
            # newSemester help page
            newSemester = discord.Embed(colour=discord.Colour.red())
            newSemester.set_author(name='Help | newSemester', icon_url=huskyBotIconURL)
            newSemester.set_thumbnail(url=questionMarkImageURL)
            newSemester.add_field(name='Command', value='`.newSemester`', inline=False)
            newSemester.add_field(name='Example', value='`.newSemester`', inline=False)
            newSemester.add_field(name='Permissions', value='Administrator', inline=False)
            newSemester.add_field(name='Note', value="Will remove all courses from every member in the server.", inline=False)
            newSemester.add_field(name='Purpose', value='To initiate a fresh restart for all members and avoid having old members in courses they are not currently taking.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=newSemester)  # sends user a DM
            return
        if admin and selection == 'CLEARCOURSES':
            # clearCourses help page
            clearCourses = discord.Embed(colour=discord.Colour.red())
            clearCourses.set_author(name='Help | clearCourses', icon_url=huskyBotIconURL)
            clearCourses.set_thumbnail(url=questionMarkImageURL)
            clearCourses.add_field(name='Command', value='`.clearCourses [member]`', inline=False)
            clearCourses.add_field(name='Example', value='`.clearCourses @User123#1234`', inline=False)
            clearCourses.add_field(name='Permissions', value='Administrator', inline=False)
            clearCourses.add_field(name='Note', value="Will remove all courses from a member.", inline=False)
            clearCourses.add_field(name='Purpose', value='Allows for easy deletion of all course roles from a user for specific cases especially spam.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=clearCourses)  # sends user a DM
            return
        if admin and selection == 'CLEARREACTIONS':
            # clearReactions help page
            clearReactions = discord.Embed(colour=discord.Colour.red())
            clearReactions.set_author(name='Help | clearReactions', icon_url=huskyBotIconURL)
            clearReactions.set_thumbnail(url=questionMarkImageURL)
            clearReactions.add_field(name='Command', value='`.clearReactions [member]`', inline=False)
            clearReactions.add_field(name='Example', value='`.clearReactions @User123#1234`', inline=False)
            clearReactions.add_field(name='Permissions', value='Administrator', inline=False)
            clearReactions.add_field(name='Note', value="Will remove all reactions given by a member in the `#course-registration` channel. There is a short timeout every 5 reactions removed if they are tied to a reaction role which the user currently has.", inline=False)
            clearReactions.add_field(name='Purpose', value='Allows for easy removal of all reactions from a user in `#course-registration` for specific cases especially spam.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=clearReactions)  # sends user a DM
            return
        if admin and selection == 'NEWEMBED':
            # newEmbed help page
            newEmbed = discord.Embed(colour=discord.Colour.red())
            newEmbed.set_author(name='Help | newEmbed', icon_url=huskyBotIconURL)
            newEmbed.set_thumbnail(url=questionMarkImageURL)
            newEmbed.add_field(name='Command', value='`.newEmbed [embed-title], [image-url]`', inline=False)
            newEmbed.add_field(name='Example', value='`.newEmbed Add/Remove ABCD courses, https://imgur.com/PKev2zr.png`', inline=False)
            newEmbed.add_field(name='Permissions', value='Administrator', inline=False)
            newEmbed.add_field(name='Note', value="Will create a new embedded message with the given title and image. Will also send a course description stub message which can be modified to describe which reactions correspond to each course.", inline=False)
            newEmbed.add_field(name='Purpose', value='Allows user to create embedded messages in `#course-registration` to use as differentiable sections and reaction role messages.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=newEmbed)  # sends user a DM
            return
        if admin and selection == 'EDITEMBEDIMAGE':
            # editEmbedImage help page
            editEmbedImage = discord.Embed(colour=discord.Colour.red())
            editEmbedImage.set_author(name='Help | editEmbedImage', icon_url=huskyBotIconURL)
            editEmbedImage.set_thumbnail(url=questionMarkImageURL)
            editEmbedImage.add_field(name='Command', value='`.editEmbedImage [message] [image-url]`', inline=False)
            editEmbedImage.add_field(name='Example', value='`.editEmbedImage 123456789876543210 https://imgur.com/7obLnAa.png`', inline=False)
            editEmbedImage.add_field(name='Permissions', value='Administrator', inline=False)
            editEmbedImage.add_field(name='Note', value="Will set the embedded message's image to be the provided url.", inline=False)
            editEmbedImage.add_field(name='Purpose', value="Allows user to update any previously sent embedded message's image without resending a new one. Allows for easy updates to update section images if a user decides a new one is needed.", inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=editEmbedImage)  # sends user a DM
            return
        if admin and selection == 'EDITEMBEDTITLE':
            # editEmbedTitle help page
            editEmbedTitle = discord.Embed(colour=discord.Colour.red())
            editEmbedTitle.set_author(name='Help | editEmbedTitle', icon_url=huskyBotIconURL)
            editEmbedTitle.set_thumbnail(url=questionMarkImageURL)
            editEmbedTitle.add_field(name='Command', value='`.editEmbedTitle [message] [title]`', inline=False)
            editEmbedTitle.add_field(name='Example', value='`.editEmbedTitle 123456789876543210 New Title`', inline=False)
            editEmbedTitle.add_field(name='Permissions', value='Administrator', inline=False)
            editEmbedTitle.add_field(name='Note', value="Will set the embedded message's title to be the provided title.", inline=False)
            editEmbedTitle.add_field(name='Purpose', value="Allows users to update any previously sent embedded message's title without resending a new one. Allows for easy updates to update section title if a user decides a new one is needed.", inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=editEmbedTitle)  # sends user a DM
            return
        if admin and selection == 'EDITCOURSECONTENT':
            # editCourseContent help page
            editCourseContent = discord.Embed(colour=discord.Colour.red())
            editCourseContent.set_author(name='Help | editCourseContent', icon_url=huskyBotIconURL)
            editCourseContent.set_thumbnail(url=questionMarkImageURL)
            editCourseContent.add_field(name='Command', value='`.editCourseContent [message] [content]`', inline=False)
            editCourseContent.add_field(name='Example', value=r'`.editCourseContent 123456789876543210 blah blah blah `\n` blah blah blah`', inline=False)
            editCourseContent.add_field(name='Permissions', value='Administrator', inline=False)
            editCourseContent.add_field(name='Note', value=("Will edit any message sent by Husky Bot with the new content.\n"
                                                            "This will **overwrite** the content, **not** add to it.\n"
                                                            r"Any newlines must be indicated by typing `\n`, `shift-enter` will be ignored as a newline.""\n"
                                                            "This will not edit the content of an embedded message."), inline=False)
            editCourseContent.add_field(name='Purpose', value="Allows users to update any course descriptions in `#course-registration` in the case there is new content they need to add or fix.", inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=editCourseContent)  # sends user a DM
            return

        if admin and selection == 'CCS':
            # course creation shortcuts help page
            ccs = discord.Embed(
                desccsiption="To see a page, just add the page name after the `.help` command.\n"
                             "Like this: `.help newCourse`",
                colour=discord.Colour.red())
            ccs.set_author(name='Help | Course Registration Commands', icon_url=huskyBotIconURL)
            ccs.set_thumbnail(url=questionMarkImageURL)
            ccs.add_field(name='Commands', value='`.newCourse`, `.newCourseReaction`, `.newCourseComplete`,', inline=False)  # available commands
            ccs.add_field(name='Page newCourse | New Course', value='How to use the `.newCourse` Command!', inline=False)  # newCourse documentation
            ccs.add_field(name='Page newCourseReaction | New Course Reaction', value='How to use the `.newCourseReaction` Command!', inline=False)  # newCourseReaction documentation
            ccs.add_field(name='Page newCourseComplete | New Course Complete', value='How to use the `.newCourseComplete` Command!', inline=False)  # newCourseComplete documentation
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=ccs)  # sends user a DM
            return
        if admin and selection == 'NEWCOURSE':
            # newCourse help page
            newCourse = discord.Embed(colour=discord.Colour.red())
            newCourse.set_author(name='Help | newCourse', icon_url=huskyBotIconURL)
            newCourse.set_thumbnail(url=questionMarkImageURL)
            newCourse.add_field(name='Command', value='`.newCourse [course-name] [channel-name]`', inline=False)
            newCourse.add_field(name='Example', value='`.newCourse ABCD-1234 course-abcd` or `.newCourse AB-1234 course ab` or `.newCourse ABCD-12XX course-abcd` or `.newCourse AB-12XX course-ab`', inline=False)
            newCourse.add_field(name='Permissions', value='Administrator', inline=False)
            newCourse.add_field(name='Note', value=("Will create a new role with the given course-name if it is the correct format.\n"
                                                    "Will hoist the role to the appropriate position in the hierarchy with the greater course number placing higher.\n"
                                                    "Will create a new channel under the appropriate category.\n"
                                                    "Will position the channel to the appropriate position in the hierarchy relative to the other courses with the lower course number placing higher than the greater course numbers.\n"
                                                    "If it is a course for a new category it will create the category and then place the channel inside.\n"
                                                    "Will setup permissions not allowing members with the Not Registered role to read the messages while only allowing members with the specified course role to read messages.\n"
                                                    "Cannot create a newCourse if there is an existing role for it."), inline=False)
            newCourse.add_field(name='Purpose', value='A shortcut which does not require the user to manually create a role and channel, worry about positioning, or permissions.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=newCourse)  # sends user a DM
            return
        if admin and selection == 'NEWCOURSEREACTION':
            # newCourseReaction help page
            newCourseReaction = discord.Embed(colour=discord.Colour.red())
            newCourseReaction.set_author(name='Help | newCourseReaction', icon_url=huskyBotIconURL)
            newCourseReaction.set_thumbnail(url=questionMarkImageURL)
            newCourseReaction.add_field(name='Command', value='`.newCourseReaction [course-role] [course-description]`', inline=False)
            newCourseReaction.add_field(name='Example', value='`.newCourseReaction @ABCD-1234 abcd description`', inline=False)
            newCourseReaction.add_field(name='Permissions', value='Administrator', inline=False)
            newCourseReaction.add_field(name='Note', value=("Given course-role must already exist.\n"
                                                            "Will find the reaction role embedded message category associated with the course and create a reaction role for the new course with the next letter in the alphabet.\n"
                                                            "Will edit the course description so that the new course's description is listed, and will be placed in the correct order relative to the other courses with the lower course number being listed higher.\n"
                                                            "Will not execute if 26 letters already exist on the category's reaction role message.\n"
                                                            "Will not execute if the given course already has a reaction role on the given message.\n"), inline=False)
            newCourseReaction.add_field(name='Purpose', value='A shortcut which does not require the user to manually create a reaction role for the course by giving specific information about channel, message_id, reaction and then manually edit another HuskyBot message for the course-description.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=newCourseReaction)  # sends user a DM
            return
        if admin and selection == 'NEWCOURSECOMPLETE':
            # newCourseComplete help page
            newCourseComplete = discord.Embed(colour=discord.Colour.red())
            newCourseComplete.set_author(name='Help | newCourseComplete', icon_url=huskyBotIconURL)
            newCourseComplete.set_thumbnail(url=questionMarkImageURL)
            newCourseComplete.add_field(name='Command', value='`.newCourseComplete [course-role] [channel-description], [course-description]`', inline=False)
            newCourseComplete.add_field(name='Example', value='`.newCourseComplete ABCD-1234 abcd channel, abcd description`', inline=False)
            newCourseComplete.add_field(name='Permissions', value='Administrator', inline=False)
            newCourseComplete.add_field(name='Note', value="Must have a comma to separate the channel description and course description. (All other specifics pertaining to `.newCourse` and `.newCourseReaction`)", inline=False)
            newCourseComplete.add_field(name='Purpose', value='An all-in-one shortcut allowing the user to automate all the task of creating a new course carrying out the specifics of `.newCourse` followed by `.newCourseReaction`.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=newCourseComplete)  # sends user a DM
            return

        if mod and selection == 'STATS':
            # stats help page
            stats = discord.Embed(
                description="To see a page, just add the page name after the `.help` command.\n"
                            "Like this: `.help serverinfo`",
                colour=discord.Colour.red())
            stats.set_author(name='Help | Stats Commands', icon_url=huskyBotIconURL)
            stats.set_thumbnail(url=questionMarkImageURL)
            stats.add_field(name='Commands', value='`.serverinfo`, `.orderedListMembers`, `.joinNo`, `.whois`', inline=False)  # available commands
            stats.add_field(name='Page serverinfo | Server Info', value='How to use the `.serverinfo` Command!', inline=False)  # serverinfo documentation
            stats.add_field(name='Page orderedListMembers | Ordered List of Members', value='How to use the `.orderedListMembers` Command!', inline=False)  # orderedListMembers documentation
            stats.add_field(name='Page joinNo | Member Join No', value='How to use the `.joinNo` Command!', inline=False)  # joinNo documentation
            stats.add_field(name='Page whois | Member Info', value='How to use the `.whois` Command!', inline=False)  # whois documentation
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=stats)  # sends user a DM
            return
        if mod and selection == 'SERVERINFO':
            # serverinfo help page
            serverinfo = discord.Embed(colour=discord.Colour.red())
            serverinfo.set_author(name='Help | serverinfo', icon_url=huskyBotIconURL)
            serverinfo.set_thumbnail(url=questionMarkImageURL)
            serverinfo.add_field(name='Command', value='`.serverinfo`', inline=False)
            serverinfo.add_field(name='Example', value='`.serverinfo`', inline=False)
            serverinfo.add_field(name='Permissions', value='Administrator or Moderator', inline=False)
            serverinfo.add_field(name='Note', value="None", inline=False)
            serverinfo.add_field(name='Purpose', value=("Returns an embedded messages with information about the current state of the server. \n"
                                                        "Includes: Server ID, Date Server Created, Server Icon, Server Owner, Region, "
                                                        "Number of Channel Categories, Number of Text Channels, Number of Voice Channel, "
                                                        "Number of Role, Number of Member, Number of Human, Number of Bot, "
                                                        "Number of users currently online, Number of users currently idle, "
                                                        "Number of users currently on do not disturb, Number of user currently on mobile, "
                                                        "Number of user who made a New Account (<1 day old account) before joining the server, "
                                                        "Number of emojis, Verification Level, Number of Active Invites, 2FA State"), inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=serverinfo)  # sends user a DM
            return
        if mod and selection == 'ORDEREDLISTMEMBERS':
            # orderedListMembers help page
            orderedListMembers = discord.Embed(colour=discord.Colour.red())
            orderedListMembers.set_author(name='Help | orderedListMembers', icon_url=huskyBotIconURL)
            orderedListMembers.set_thumbnail(url=questionMarkImageURL)
            orderedListMembers.add_field(name='Command', value='`.orderedListMembers [number of members] [outputType]`', inline=False)
            orderedListMembers.add_field(name='Example', value='`.orderedListMembers 30 mention` or `.orderedListMembers 50` or `.orderedListMembers`', inline=False)
            orderedListMembers.add_field(name='Permissions', value='Administrator or Moderator', inline=False)
            orderedListMembers.add_field(name='Note', value=("Will default to 10 members if no arguments are given. \n"
                                                             "If there are less than 10 members, it will get all the members. \n"
                                                             "Will default to showing nicknames if no output type is given. \n"
                                                             "OutputTypes: nick/nickname (user's nickname or username if no nickname), name (user's username), mention (user mentioned) \n"
                                                             "Includes bot accounts."), inline=False)
            orderedListMembers.add_field(name='Purpose', value=("Returns a list of members, in an embedded message by order of the date they joined the server."), inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=orderedListMembers)  # sends user a DM
            return
        if mod and selection == 'JOINNO':
            # joinNo help page
            joinNo = discord.Embed(colour=discord.Colour.red())
            joinNo.set_author(name='Help | joinNo', icon_url=huskyBotIconURL)
            joinNo.set_thumbnail(url=questionMarkImageURL)
            joinNo.add_field(name='Command', value='`.joinNo [number]`', inline=False)
            joinNo.add_field(name='Example', value='`.joinNo 50`', inline=False)
            joinNo.add_field(name='Permissions', value='Administrator or Moderator', inline=False)
            joinNo.add_field(name='Note', value="Will send error messages to guide the user if the given number is not within the range of members in the server. Includes bot accounts.", inline=False)
            joinNo.add_field(name='Purpose', value=("Returns an embedded messages with information about the current state of the server. \n"
                                                    "Includes: Member ID, Member Name Including Discriminator, Mentioned member, "
                                                    "Profile Picture, Current Online Status, Date the member joined, "
                                                    "Member's join position in the server, Date the member created a Discord Account, "
                                                    "The roles the member has in the server and the number of roles, "
                                                    "Permissions that the member has in the server overall, "
                                                    "Member's color via the embedded message color"), inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=joinNo)  # sends user a DM
            return
        if mod and (selection == 'WHOIS' or selection == '9'):
            # whois help page
            whois = discord.Embed(colour=discord.Colour.red())
            whois.set_author(name='Help | whois', icon_url=huskyBotIconURL)
            whois.set_thumbnail(url=questionMarkImageURL)
            whois.add_field(name='Command', value='`.whois [member_name]`', inline=False)
            whois.add_field(name='Aliases', value='`.whoam`', inline=False)
            whois.add_field(name='Example', value='`.whois discordUser19` or `.whoam I` or `.whois`', inline=False)
            whois.add_field(name='Permissions', value='Administrator/Moderator and Everyone', inline=False)
            whois.add_field(name='Note', value=("Admins can find info about any member."
                                                "Non-admin/mod members can use this command to find out information about themselves."
                                                'Will default to the user who sent the command if no arguments are given or the letter "I" is given.'
                                                "Will search for members with spaces, is case-insensitive, and will check if the argument is within another member name."), inline=False)
            whois.add_field(name='Purpose', value=("Returns an embedded messages with information about the current state of the server. \n"
                                                   "Includes: Member ID, Member Name Including Discriminator, Mentioned member, "
                                                   "Profile Picture, Current Online Status, Date the member joined, "
                                                   "Member's join position in the server, Date the member created a Discord Account, "
                                                   "The roles the member has in the server and the number of roles, "
                                                   "Permissions that the member has in the server overall, "
                                                   "Member's color via the embedded message color"), inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=whois)  # sends user a DM
            return

        if mod and selection == '0':
            # clear help page
            clear = discord.Embed(colour=discord.Colour.red())
            clear.set_author(name='Help | clear', icon_url=huskyBotIconURL)
            clear.set_thumbnail(url=questionMarkImageURL)
            clear.add_field(name='Command', value='`.clear [number] [member]`', inline=False)
            clear.add_field(name='Example', value='`.clear 20` or `.clear 10 @member#1234`', inline=False)
            clear.add_field(name='Permissions', value='Manage Messages', inline=False)
            clear.add_field(name='Note', value=('Must be greater than 0.'), inline=False)
            clear.add_field(name='Purpose', value='Clears the last given number of messages in the channel or the ones specifically from a given member.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=clear)  # sends user a DM
            return

        if selection == '1':
            # reminder help page
            reminder = discord.Embed(colour=discord.Colour.red())
            reminder.set_author(name='Help | Reminder', icon_url=huskyBotIconURL)
            reminder.set_thumbnail(url=questionMarkImageURL)
            reminder.add_field(name='Command', value='`.reminder [insert-reminder-here] in [number] [unit-of-time]`', inline=False)
            reminder.add_field(name='Example', value='`.reminder get laundry in 32 mins`', inline=False)
            reminder.add_field(name='Note', value='"in" is a manditory word that __must__ exist between the reminder and the time. (Case-insensitive)', inline=False)
            reminder.add_field(name='Unit of time possibilites', value='second, seconds, secs, sec, s, minutes, mins, min, m, hour, hours, hr, hrs, h, day, days, d, week, weeks, w', inline=False)
            reminder.add_field(name='Purpose', value='Confirmation message will be sent and user will receive a DM in the specified duration of time.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=reminder)  # sends user a DM
            return

        if selection == '2':
            # hours help page
            hours = discord.Embed(colour=discord.Colour.red())
            hours.set_author(name='Help | Hours', icon_url=huskyBotIconURL)
            hours.set_thumbnail(url=questionMarkImageURL)
            hours.add_field(name='Command', value='`.hours [location], [day]`', inline=False)
            hours.add_field(name='Example', value='`.hours stwest, monday`', inline=False)
            hours.add_field(name='Note', value=('Day is optional. If no day is provided, the current day is used by default.\n'
                                                'A location can be mulitple words and can be valid under multiple aliases.\n'
                                                'A comma __must__ be used to separate the location and day. (Case-insensitive)'), inline=False)
            hours.add_field(name='Possible Days', value=("Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, "
                                                         "Sun, Mon, Tues, Wed, Thurs, Fri, Sat, Tomorrow, S, U, M, T, W, R, F, "
                                                         "Tu, Tue, Tues, Th, Thu, Thurs"), inline=False)
            hours.add_field(name='Supported Locations (as of Dec 2019)', value=("Amelia's Taqueria, Argo Tea, Boston Shawarma, Café 716, "
                                                                                "Café Crossing, Cappy's, Chicken Lou's, College Convenience, "
                                                                                "CVS, Dominos, Faculty Club, Gyroscope, International Village, "
                                                                                "Kigo Kitchen, Kung Fu Tea, Outtakes, Panera Bread, Pho and I, "
                                                                                "Popeyes Louisiana Kitchen, Qdoba, Rebecca's, Resmail, "
                                                                                "Star Market, Starbucks, Stetson East, Stetson West, Subway, "
                                                                                "Sweet Tomatoes, Symphony Market, Tatte, The Egg Shoppe, "
                                                                                "The Market, The West End, Tú Taco, Uburger, "
                                                                                "University House Of Pizza, Wendy's, Whole Foods, Wings Over, "
                                                                                "Wollaston's Market, Wollaston's Market West Village."), inline=False)
            hours.add_field(name='Purpose', value=("Says the hours of operation of select locations and determines whether it's OPEN or CLOSED."
                                                   "Specifies minutes left until closing/opening if less than 1 hour remaining."), inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=hours)  # sends user a DM
            return
        
        if selection == '3':
            # hours help page
            hours = discord.Embed(colour=discord.Colour.red())
            hours.set_author(name='Help | Open', icon_url=huskyBotIconURL)
            hours.set_thumbnail(url=questionMarkImageURL)
            hours.add_field(name='Command', value='`.open [optional-sort-arg]`', inline=False)
            hours.add_field(name='Example', value='`.open` or `.open sort`', inline=False)
            hours.add_field(name='Note', value=("The argument is optional. If none is provided it will display the locations in alphabetical order. "
                                                "If given, it will display them in order of time to close."), inline=False)
            hours.add_field(name='Purpose', value=("To see all the available locations at once in either alphabetical order or order of time to close."), inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=hours)  # sends user a DM
            return

        if selection == '4':
            # ice-cream help page
            ice_cream = discord.Embed(colour=discord.Colour.red())
            ice_cream.set_author(name='Help | Ice Cream', icon_url=huskyBotIconURL)
            ice_cream.set_thumbnail(url=questionMarkImageURL)
            ice_cream.add_field(name='Command', value='`.icecream [day]`', inline=False)
            ice_cream.add_field(name='Example', value='`.icecream monday`', inline=False)
            ice_cream.add_field(name='Note', value='Day is optional. If no day is provided, the current day will be used by default.', inline=False)
            ice_cream.add_field(name='Purpose', value=('Displays what the current ice cream flavors are available any day from the Northeastern Dining Halls.'), inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=ice_cream)  # sends user a DM
            return

        if selection == '5':
            # day date help page
            day_date = discord.Embed(colour=discord.Colour.red())
            day_date.set_author(name='Help | Day Date', icon_url=huskyBotIconURL)
            day_date.set_thumbnail(url=questionMarkImageURL)
            day_date.add_field(name='Command', value='`.day [date]`', inline=False)
            day_date.add_field(name='Example', value='`.day 9/1/2022` or `.day Sept 1 2022`', inline=False)
            day_date.add_field(name='Note', value='If year is not provided, current year is used by default. However, year is manditory for MM/DD/YYYY format. Year must be less than 10000', inline=False)
            day_date.add_field(name='Date Formats', value='MM/DD/YYYY, Month Day Year, Month Day', inline=False)
            day_date.add_field(name='Purpose', value='Determines the day of any given date', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=day_date)  # sends user a DM
            return

        if selection == '6':
            # music help page
            music = discord.Embed(colour=discord.Colour.red())
            music.set_author(name='Help | Music', icon_url=huskyBotIconURL)
            music.set_thumbnail(url=questionMarkImageURL)
            music.add_field(name='Commands', value='`.join`, `.play`, `.pause`, `.resume`, `.skip`, `.queue`, `.display_queue`, `.leave`', inline=False)
            music.add_field(name='.join', value='Joins the voice channel the user is currently in', inline=False)
            music.add_field(name='.play', value='Plays music when given either a name or a url', inline=False)
            music.add_field(name='.pause', value=' Pauses current music', inline=False)
            music.add_field(name='.resume', value='Resumes current music', inline=False)
            music.add_field(name='.skip', value='Skips current music. Stops music if only 1 song left.', inline=False)
            music.add_field(name='.queue', value='Adds a song to the queue', inline=False)
            music.add_field(name='.display_queue', value="Displays the bot's current music queue", inline=False)
            music.add_field(name='.leave', value='Bot leaves the voice channel', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=music)  # sends user a DM
            return

        if selection == '7':
            # miscellaneous help page
            misc = discord.Embed(colour=discord.Colour.red())
            misc.set_author(name='Help | Miscellaneous', icon_url=huskyBotIconURL)
            misc.set_thumbnail(url=questionMarkImageURL)
            misc.add_field(name='Commands', value='`.ping`, `.echo`, `.flip`, `.menu`, `.invite`', inline=False)
            misc.add_field(name='.ping', value='Returns pong!', inline=False)
            misc.add_field(name='.echo', value='Repeats anything the user says after the given command', inline=False)
            misc.add_field(name='.flip', value='Flips a coin and says the result (Heads/Tails)', inline=False)
            misc.add_field(name='.menu', value="Generates a link to Northeastern's menu.", inline=False)
            misc.add_field(name='.invite', value='Generates an invite link to the NU Discord Server.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=misc)  # sends user a DM
            return

        if selection == '10':
            # playing help page
            playing = discord.Embed(colour=discord.Colour.red())
            playing.set_author(name='Help | Playing', icon_url=huskyBotIconURL)
            playing.set_thumbnail(url=questionMarkImageURL)
            playing.add_field(name='Command', value='`.playing [activity_name]`', inline=False)
            playing.add_field(name='Example', value='`.playing spotify`', inline=False)
            playing.add_field(name='Note', value='Any activity containing the keyword will be selected (not an exact match). So .playing league would find both League of Legends and Rocket League, for example.', inline=False)
            playing.add_field(name='Purpose', value='Allows for the user to find all the members in a server that is playing a certain activity.', inline=False)
            await ctx.send(f"Check your DM {author.mention}!", delete_after=5)
            await author.send(embed=playing)  # sends user a DM
            return

        await ctx.send(f"Your selection: {args[0]} was not recognized. Try again.", delete_after=5)


def setup(client):
    client.add_cog(Help(client))
