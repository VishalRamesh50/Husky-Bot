## Welcome Message
![welcome-pic](https://i.imgur.com/l4ObKiR.png) \
A member is given the "Not Registered" role on join.

## Auto-Member Registration Detection and Handling
A member is required to have the following 3 following types of roles in order to be considered "Registered":
- **Year**
  - Freshman
  - Sophomore
  - Junior
  - Middler
  - Senior
  - Grad Student
  - NUly Admitted
- **School/Major**
  - EXPLORE
  - CCIS
  - COE
  - BCHS
  - CAMD
  - DMSB
  - COS
  - CSSH

Once a member (not a bot) has all 3, the "Not Registered" Role will be removed. If not all 3 are present the "Not Registered" Role will be assigned.

## Aoun
### Set Cooldown
**Command:** `.set_a_cooldown <cooldown>` \
**Aliases:** `.setACooldown` \
**Example:** `.set_a_cooldown 30` \
**Permissions:** Admin or Moderator \
**Note:** Given cooldown is in seconds and must be less than 900. \
**Purpose:** Sets the cooldown rate between when aoun images should spawn when mentioned to avoid being spammed.

### Reset Cooldown
**Command:** `.reset_a_cooldown` \
**Aliases:** `.resetACooldown` \
**Example:** `.reset_a_cooldown` \
**Permissions:** Admin or Moderator \
**Purpose:** Resets the cooldown rate back to the default (which is 5 seconds).

## Clear
**Command:** `.clear [number] [member]` \
**Example:** `.clear` or `.clear 20` or `.clear 10 @member#1234` \
**Permissions:** Admin or Moderator \
**Note:** If no number is given the last sent message is deleted. Number must be greater than 0. \
**Purpose:** Clears the last given number of messages in the channel or the ones specifically from a given member.

## Course Registration

## Course Cleanup
### New Semester
**Command:** `.new_semester` \
**Aliases:** `.newSemester` \
**Example:** `.new_semester` \
**Permissions:** Administrator \
**Note:** Will remove all courses from every member and removes all reaction channels for courses. \
**Purpose:** To initiate a fresh restart for all members and avoid having old members in courses they are not currently taking.

### Auto Course Reactions
**Command:** `.auto_course_reactions` \
**Aliases:** `.autoCourseReactions` \
**Example:** `.auto_course_reactions` \
**Permissions:** Administrator \
**Note:** This assumes the format of the course content is like:
:reaction1: -> Course1 Description (CRSN-1234)\n
:reaction2: -> Course2 Description (CRSN-4321) \
**Purpose:** To automate creating course reaction channels if only embeds and content exist. This might happen when a completely new course registration page needs to be made or if resetting the semester also gets rid of all the reaction channels.

### Clear Courses
**Command:** `.clear_courses <member>` \
**Aliases:** `.clearCourses` \
**Example:** `.clear_courses @member#1234` \
**Permissions:** Administrator \
**Note:** Will remove all courses from a member. \
**Purpose:** Allows for easy unerollment from all courses for a member, useful when either starting a new semester or in cases of spam.

### Clear Reactions
**Command:** `.clear_reactions <member>` \
**Aliases:** `.clearReactions` \
**Example:** `.clear_reactions @member#1234` \
**Permissions:** Administrator \
**Note:** Will remove all course reaction channels added by a member. There is a short ratelimit every 5 reactions removed due to modifying channel permissions. \
**Purpose:** Allows for easy removal of all course reaction channels from a member, useful when either starting a new semester or in cases of spam.

## Course Content
### Course Embed
**Command:** `.course_embed <course-category> <img-url>` \
**Aliases:** `.courseEmbed`, `.newCourseEmbed` \
**Example:** `.course_embed HSKY https://i.imgur.com/7obLnAa.png` \
**Permissions:** Administrator \
**Purpose:** Creates reaction role templates for new categories.

### Edit Embed Image
**Command:** `.edit_embed_image <message> <image-url>` \
**Aliases:** `.editEmbedImage` \
**Example:** `.edit_embed_image 123456789876543210 https://imgur.com/7obLnAa.png` \
**Permissions:** Administrator \
**Note:** Will set the embedded message's image to be the provided url. \
**Purpose:** Allows user to easily update any embedded message's image. Useful when a course category needs a new image and new message can't be sent without messing up the order.

### Edit Embed Title
**Command:** `.edit_embed_title <message> <title>` \
**Aliases:** `.editEmbedTitle` \
**Example:** `.edit_embed_title 123456789876543210 New Title` \
**Permissions:** Administrator \
**Purpose:** Allows user to easily change the title of any embedded message. Useful when a course category's title needs to be modified without sending a new message.

### Edit Course Content
**Command:** `.edit_course_content <message> <content>` \
**Aliases:** `.editCourseContent` \
**Example:** 
```
.edit_course_content 123456789876543210
blah blah line 1 blah
blah blah line 2 blah
blah blah line 3 blah
```
**Permissions:** Administrator \
**Note:**
- Will edit any message sent by Husky Bot with the new content.
- This will **overwrite** the content, **not** add to it.
- The message will be edited as it is in the text box. `shift-enter` is honored as a newline.
- This will not edit the content of an message with an embedded message.

**Purpose:** Grants the ability to edit any message with new content, especially category descriptions whenever content needs to be fixed or added to.

### Navigation Embed
**Command:** `.nav_embed` \
**Aliases:** `.navEmbed` \
**Example:** `.nav_embed` \
**Permissions:** Administrator \
**Purpose:** Creates a navigation embed filled with useful links to jump to categories in alphabetical order and other useful content in `#course-registration`.

## Course Selection

### Toggle AutoDelete
**Command:** `.toggle_ad` \
**Aliases:** `.toggleAD` \
**Example:** `.toggle_ad` \
**Permissions:** Administrator \
**Note:** Toggles whether to delete messages sent by HuskyBot in `#course-registration` or not. \
**Purpose:** Allows for user to toggle off auto-delete when creating new messages via HuskyBot in `#course-registration` and then toggle it back on for general use cleanup.

### Toggle Courses
**Command:** `.choose <role-name>` \
**Example:** `.choose CS-2500` or `.choose cs 2500` or `.choose spring green` \
**Permissions:** Administrator & Everyone \
**Note:**
- Non-admin users can only toggle roles from `#course-regisration` and use it there.
- Course/role names are case-insensitive, spaces are allowed, and courses do not require a '-' even if it is in the name.

**Purpose:** Toggle `#course-registration` roles without having to search for their reactions in the large channel.

## Create Course

### New Course
**Command:** `.new_course <course-name> <channel-name>` \
**Aliases:** `.newCourse` \
**Example:** `.new_course ABCD-1234 course-abcd` or `.new_course AB-1234 course ab` or `.new_course ABCD-12XX course-abcd` or `.new_course AB-12XX course-ab` \
**Permissions:** Administrator \
**Note:**
- Will not proceed if the role already exists.
- Expects a course name in the format: `ABCD-1234`/`AB-1234`/`ABCD-12XX`/`AB-12XX`
- Will create a new private channel where only members enrolled in the course can access it.
- Will order the channel where the greater course number is at the top.
- Will create a new category for the course if one does not already exist.

**Purpose:** A shortcut which does not require the user to manually create a role and channel, worry about positioning, or permissions.

### New Course Reaction
**Command:** `.new_course_reaction <course-role> <course-description>` \
**Aliases:** `.newCourseReaction` \
**Example:** `.new_course_reaction @ABCD-1234 abcd description` \
**Permissions:** Administrator \
**Note:**
- Will not execute if course-role does not exist.
- Will not execute if 26 letters already exist on the category's reaction role message.
- Will not execute if the given course already has a reaction channel on the given message.
- Will create a reaction channel for the associated category and use the next letter it's trigger.
- Will edit the category description so that the new course's description is listed relative to the other courses with the lower course number being listed higher.

**Purpose:** A shortcut which does not require the user to manually create a new reaction role and provide all the necessary metadata. Also saves user from updating category description.

### New Course Complete
**Command:** `.new_course_complete [course-role] [channel-description], [course-description]` \
**Aliases:** `.newCourseComplete` \
**Example:** `.new_course_complete ABCD-1234 abcd channel, abcd description` \
**Permissions:** Administrator \
**Note:** Must have a comma to separate the channel description and course description. \
**Purpose:** An all-in-one shortcut allowing the user to automate all the task of creating a new course carrying out the specifics of [new_course](docs/DOCUMENTATION.md#new-course) followed by [new_course_reaction](docs/DOCUMENTATION.md#new-course-reaction).

## Hall Of Fame
**Command:** `.set_hof_threshold <threshold>` \
**Aliases:**: `.setHOFThreshold` \
**Example:** `.set_hof_threshold 3` \
**Permissions:** Administrator or Moderator \
**Purpose:** Can set the value of the number of reactions needed to trigger the hall of fame message without restarting the bot.

## Loader

### Load
**Command:** `.load <cog-name>` \
**Example:** `.load suggest` \
**Permissions:** Administrator \
**Note:** The full path of the cog after `/cogs` must be provided where `/` is substituted with `.`. description. So to load the create course cog for example, you would need `.load course_registration.create_course` \
**Purpose:** Allows to load cogs at will without restarting the bot.

### Unload
**Command:** `.unload <cog-name>` \
**Example:** `.unload suggest` \
**Permissions:** Administrator \
**Note:** The full path of the cog after `/cogs` must be provided where `/` is substituted with `.` description. So to load the create course cog for example, you would need `.unload course_registration.create_course` \
**Purpose:** Allows to unload cogs at will without restarting the bot.

## Reaction

## Reaction Roles
### Adding New Reaction Role
**Command:** `.newrr <channel> <message_id> <reaction/emoji> <role>` \
**Example:** `.newrr #course-registration 123456789876543210 💻 @CCIS` \
**Permissions:** Administrator \
**Purpose:** Allows for the user to select a specific message that users can react to with a chosen emoji to get assigned a role and unreact to remove the role.

### Fetching Reaction Role Information
**Command:** `.fetchrr <message_id>` \
**Example:** `.fetchrr 123456789876543210` \
**Permissions:** Administrator \
**Purpose:** Fetches all the keys, reaction, and roles corresponding with each reaction role for the given message id.

### Removing a Reaction Role
**Command:** `.removerr <key>` \
**Example:** `.removerr F0xUOpxMv` \
**Permissions:** Administrator \
**Note:** Given key must be a valid key. Each reaction role is assigned a unique key and can be found in the embedded message upon creation of the reaction role or by using the `.fetchrr` command. \
**Purpose:** Allows for the user to delete any reaction role by giving the unique key.

### Removing All Reaction Roles for Message
**Command:** `.removeallrr <message_id>` \
**Example:** `.removeallrr 123456789876543210` \
**Permissions:** Administrator \
**Purpose:** Allows for the user to delete all reaction roles from a given message at once.

## Reaction Channels
### Adding New Reaction Channel
**Command:** `.newrc <channel> <message_id> <reaction/emoji> <target-channel>` \
**Example:** `.newrc #course-registration 123456789876543210 👍 #course-1` \
**Permissions:** Administrator \
**Purpose:** Allows for the user to select a specific message that users can react to with a chosen emoji to get permission to access a channel and unreact to opt-out of the channel again.

### Fetching Reaction Channel Information
**Command:** `.fetchrr <message_id>` \
**Example:** `.fetchrr 123456789876543210` \
**Permissions:** Administrator \
**Purpose:** Fetches all the keys, reaction, and channels corresponding with each reaction channel for the given message id.

### Removing a Reaction Channel
**Command:** `.removerc <key>` \
**Example:** `.removerc F0xUOpxMv` \
**Permissions:** Administrator \
**Note:** Given key must be a valid key. Each reaction channel is assigned a unique key and can be found in the embedded message upon creation of the reaction role or by using the `.fetchrc` command. \
**Purpose:** Allows for the user to delete any reaction channel by giving the unique key.

### Removing All Reaction Channels for Message
**Command:** `.removeallrc <message_id>` \
**Example:** `.removeallrc 123456789876543210` \
**Permissions:** Administrator \
**Purpose:** Allows for the user to delete all reaction channels from a given message at once.

## Twitch

### Add Twitch
**Command:** `.add_twitch <twitch_username> [member_name]` \
**Command:** `.addTwitch` \
**Example:** `.add_twitch HuskyStreams @HuskyBot#1234` or `.add_twitch RocketLeague` \
**Permissions:** Administrator \
**Purpose:** Adds a Twitch user to a list of users being tracked and HuskyBot will send a notification any time they go live. If a discord member name is sent, their tag will show as a field in the embedded message.

### Remove Twitch
**Command:** `.remove_twitch <twitch_username>` \
**Aliases:** `.removeTwitch` \
**Example:** `.remove_twitch HuskyStreams` \
**Permissions:** Administrator \
**Purpose:** Removes a Twitch user from being tracked for when their streams go live.

### List Twitch
**Command:** `.list_twitch` \
**Example:** `.listTwitch`, `.lsTwitch` \
**Example:** `.list_twitch` \
**Permissions:** Administrator \
**Purpose:** Lists all the Twitch members currently being tracked.


## Activity
### Playing
**Command:** `.playing <activity_name>` \
**Example:** `.playing spotify` \
**Permissions:** Everyone \
**Note:** Any activity containing the keyword will be selected (not an exact match). So `.playing league` would find both League of Legends and Rocket League, for example. \
**Purpose:** Allows for the user to find all the members in a server that is playing a certain activity.

### Streaming
**Command:** `.streaming` \
**Example:** `.streaming` \
**Permissions:** Everyone \
**Purpose:** Allows a user to find all the members in a server currently streaming.

## Anonymous Modmail
### Ticket
**Command:** `.ticket` \
**Example:** `.ticket` \
**Permissions:** Everyone \
**Note:** Must be invoked in a DM. You can only have one ticket open at a time. \
**Purpose:** Allows for users to anonymously communicate with moderators. Useful for giving feedback without worrying about identity.

### Close
**Command:** `.close` \
**Example:** `.close` \
**Permissions:** Moderator \
**Purpose:** Allows moderators to close an open ticket. After this, no message sent will continue to be relayed to the other person.

## Day Date
**Command:** `.day <date>` \
**Permissions:** Everyone \
**Example:** `.day 9/1/2022` or `.day Sept 1 2022` \
**Note:** If year is not provided, current year is used by default. Year must be less than 10000 \
**Date Formats:** mm/dd/yy | mm/dd/YYYY | Month dd, YY | MonthAcronym dd, YY \
**Purpose:** Determines the day of any given date

## Hours
**Command:** `.hours <location>, [day]` \
**Example:** `.hours stwest, monday` or `.hours steast` \
**Permissions:** Everyone \
**Note:** Day is optional. If no day is provided, the current day is used by default. \
A location can be multiple words and can be valid under multiple aliases.\
A comma __must__ be used to separate the location and day. (Case-insensitive) \
**Possible Days:** Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sun, Mon, Tues, Wed, Thurs, Fri, Sat, S, U, M, T, W, R, F, Tu, Tue, Tues, Th, Thu, Thurs, Tomorrow \
**Supported Locations (as of Jan 2020):** Amelia's Taqueria, Argo Tea, Boston Shawarma, Café 716, Café Crossing, Cappy's, Chicken Lou's, College Convenience, CVS, Dominos, Faculty Club, Gyroscope, International Village, Kigo Kitchen, Kung Fu Tea, Marino Center, Outtakes, Panera Bread, Pho and I, Popeyes Louisiana Kitchen, Qdoba, Rebecca's, Resmail, SquashBusters, Star Market, Starbucks, Stetson East, Stetson West, Subway, Sweet Tomatoes, Symphony Market, Tatte, The Egg Shoppe, The Market, The West End, Tú Taco, Uburger, University House Of Pizza, Wendy's, Whole Foods, Wings Over, Wollaston's Market, Wollaston's Market West Village." \
**Purpose:** Says the hours of operation of select locations and determines whether it's OPEN or CLOSED. Specifies minutes left until closing/opening if less than 1 hour remaining.

## Ice Cream
**Command:** `.icecream [day]` \
**Example:** `.icecream` or `.icecream monday` \
**Permissions:** Everyone \
**Note:** Day is optional. If no day is provided, the current day will be used by default. \
**Purpose:** Displays what the current ice cream flavors are available any day from the Northeastern Dining Halls.

## Miscellaneous
**Commands:** `.ping`, `.echo`, `.flip`, `.menu`, `.invite` \
**Ping:** Sends a message which contains the Discord WebSocket protocol latency \
**Uptime:** Calculates the amount of time the bot has been up since it last started. \
**Echo:** Repeats anything the user says after the given command. \
**Flip:** Flips a coin and says the result (Heads/Tails) \
**Menu:** Sends a link to the Northeastern dining hall menu.

## Open
**Command:** `.open <sort>` \
**Example:** `.open` or `.open sort` \
**Permissions:** Everyone \
**Note:** The sort argument is optional. If none is provided it will display the locations in alphabetical order. If given, it will display them in order of time to close. \
**Purpose:** To see all the open locations at once in either alphabetical order or order of time to close.

## Reminder
**Command:** `.reminder <your-reminder> in <number> <unit-of-time>` \
**Example:** `.reminder get laundry in 32 mins` \
**Permissions:** Everyone \
**Note:** "in" is a mandatory word that must exist between the reminder and the time. \
**Unit of time possibilities:** sec, secs, second, seconds, s, min, mins, minute, minutes, m, hr, hrs, hour, hours, h, day, days, d, week, weeks, w \
**Purpose:** Sends a reminder to the user after the specified amount of time has passed.

## Stats
### Server Info
**Command:** `.serverinfo` \
**Example:** `.serverinfo` \
**Permissions:** Administrator or Moderator \
**Purpose:** Returns an embedded messages with information about the current state of the server. \
Includes:
- Server ID
- Date Server Created
- Server Icon
- Server Owner
- Region
- Number of Channel Categories
- Number of Text Channels
- Number of Voice Channels
- Number of Roles
- Number of Members
- Number of Humans
- Number of Bots
- Number of users currently online
- Number of users currently idle
- Number of users currently on do not disturb
- Number of users currently on mobile for each status
- Number of Not Registered users
- Number of users who made a New Account (<1 day old account) before joining the server
- Number of emojis
- Verification Level
- Number of Active Invites
- 2FA State

### Ordered List Members
**Command:** `.ordered_list_members [number-members] [output-type]` \
**Example:** `.orderedListMembers 30 mention` or `.orderedListMembers 50` or `.orderedListMembers`\
**Aliases:** `.orderedListMembers`, `.lsMembers`, `listMembers`, `list_members`\
**Permissions:** Administrator or Moderator \
**Note:**
- Will default to at least 10 members if no arguments are given.
- Will default to showing nicknames if no output type is given.
- OutputTypes: nick/nickname (user's nickname or username if no nickname), name (user's username), mention (user mentioned)
- Includes bot accounts.

**Purpose:** Gets a list of members by order of the date they joined the server.

### Member Info
**Command:** `.whois [member_name]` \
**Aliases:** `.whoam` \
**Example:** `.whois discordUser0000` or `.whoam I` or `.whois` \
**Permissions:** Administrator/Moderator and Everyone \
**Note:**
- Admins/mods can find info about any member.
- Non-admin/mod members can only find out information about themselves.
- Will default to the user who sent the command if no arguments are given or the letter "I" is given.
- The member search criteria is case-insensitive and does not need to be exact.

**Purpose:** Gets information about a specific user. \
Includes:
- Member ID
- Member Name Including Discriminator
- Mentioned member
- Profile Picture
- Current Online Status
- Date the member joined
- Member's join position in the server
- Date the member created a Discord Account
- The roles the member has in the server and the number of roles
- Permissions that the member has in the server overall
- Member's color via the embedded message color

### Join Position
**Command:** `.join_no <number>` \
**Example:** `.join_no 50` \
**Aliases:** `.joinNo` \
**Permissions:** Administrator or Moderator \
**Note:** Will send error messages to guide the user if the given number is not within the range of members in the server. Includes bot accounts. \
**Purpose:** Gets information about a user at a specific join position from a server. \
Includes:
- Member ID
- Member Name Including Discriminator
- Mentioned member
- Profile Picture
- Current Online Status
- Date the member joined
- Member's join position in the server
- Date the member created a Discord Account
- The roles the member has in the server and the number of roles
- Permissions that the member has in the server overall
- Member's color via the embedded message color

## Suggest
**Command:** `.suggest <your-suggestion>` \
**Example:** `.suggest add course ABCD-1234` \
**Permissions:** Everyone \
**Purpose:** Allows any member to easily make a suggestion, ping the Admins, and pin the message in the suggestions channel for visibility.
