## Welcome Message
![welcome-pic](https://i.imgur.com/l4ObKiR.png) \
A member is given the "Not Registered" role on join.

## Auto-Member Registration Detection and Handling
A member is required to have the following 3 following types of roles in order to be considered "Registered":
- **Student**
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
**Note:** Will remove all courses from every member and removes all reaction roles for courses. \
**Purpose:** To initiate a fresh restart for all members and avoid having old members in courses they are not currently taking.

### Clear Courses
**Command:** `.clear_courses <member>` \
**Aliases:** `.clearCourses` \
**Example:** `.clear_courses @member#1234` \
**Permissions:** Administrator \
**Note:** Will remove all courses from a member. \
**Purpose:** Allows for easy deletion of all course roles from a member, useful when either starting a new semester or in cases of spam.

### Clear Reactions
**Command:** `.clear_reactions <member>` \
**Aliases:** `.clearReactions` \
**Example:** `.clear_reactions @member#1234` \
**Permissions:** Administrator \
**Note:** Will remove all course reaction roles added by a member.channel. There is a short ratelimit every 5 reactions removed due to removing roles from a user. \
**Purpose:** Allows for easy removal of all course reaction roles from a member, useful when either starting a new semester or in cases of spam.

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
**Purpose:** Creates a navigation embed filled with useful links to jump to categories in alphabetical order and other useful content in the course-registration channel.

## Course Selection

### Toggle AutoDelete
**Command:** `.toggle_ad` \
**Aliases:** `.toggleAD` \
**Example:** `.toggle_ad` \
**Permissions:** Administrator \
**Note:** Will toggle the auto-delete functionality of the course registration, switching from deleting HuskyBot's messages to not. \
**Purpose:** Allows for user to toggle off auto-delete when creating new messages via HuskyBot in `#course-registration` and then toggle it back on for general use cleanup.

### Toggle Courses
**Command:** `.choose <role-name>` \
**Example:** `.choose CS-2500` or `.choose cs 2500` or `.choose spring green` \
**Permissions:** Administrator & Everyone \
**Note:**
- Non-admin users can only toggle roles from `#course-regisration` and use it there.
- Admins can toggle any role and do it anywhere.
- Role names are case-insensitive, spaces are allowed, and courses do not require a '-' even if it is in the name.

**Purpose:** Toggle `#course-registration` roles without having to search for their reactions in the large channel.

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
**Echo:** Repeats anything the user says after the given command. \
**Flip:** Flips a coin and says the result (Heads/Tails) \
**Menu:** Sends a link to the Northeastern dining hall menu. \

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

## Music
**Commands:** `.join`, `.play`,`.pause`, `.resume`, `.skip`, `.queue`, `.display_queue`, `.leave` \
**Join:** Joins the voice channel the user is currently in \
**Play:** Plays music when given either a name or a url \
**Pause:** Pauses current music \
**Resume:** Resumes current music \
**Skip:** Skips current music. Stops music if only 1 song left. \
**Queue:** Adds a song to the queue \
**Display Queue:** Displays the bot's current music queue \
**Leave:** Bot leaves the voice channel.

## Reaction Roles
### Adding New Reaction Role
**Command:** `.newrr [channel] [message_id] [reaction/emoji] [role]` \
**Example:** `.newrr #rules 123456789876543210 👍 @Student` \
**Permissions:** Administrator \
**Note:**
- Given **channel** can be in the form of a mentioned channel or just the name.
- Given **message id** must be a valid message id and a number.
- Given **emoji** must be a valid emoji in the correct form (Ex: `:thumbs_up:`).
- Given **role** can be in the form of a mentioned role or just the name.

**Purpose:** Allows for the user to select a specific message that users can react to with a chosen emoji to get assigned a role and unreact to remove the role.
### Fetching Reaction Role Information
**Command:** `.fetchrr [message_id]` \
**Example:** `.fetchrr 123456789876543210` \
**Permissions:** Administrator \
**Note:** Given message id must be a valid message id and a number. \
**Purpose:** Fetches all the keys, reaction, and roles corresponding to each reaction role for the given message id.
### Removing a Reaction Role
**Command:** `.removerr [key]` \
**Example:** `.removerr F0xUOpxMv` \
**Permissions:** Administrator \
**Note:** Given key must be a valid key. Each reaction role is assigned a unique key and can be found in the embedded message upon creation of the reaction role or by using the `.fetchrr` command. \
**Purpose:** Allows for the user to delete any reaction role by giving the unique key.
### Removing All Reaction Roles for Message
**Command:** `.removeallrr [message_id]` \
**Example:** `.removeallrr 123456789876543210` \
**Permissions:** Administrator \
**Note:** Given message id must be a valid message id and a number. \
**Purpose:** Allows for the user to delete all reaction roles from a given message at once.

## Course Creation Shortcuts
### New Course
**Command:** `.newCourse [course-name] [channel-name]` \
**Example:** `.newCourse ABCD-1234 course-abcd` or `.newCourse AB-1234 course ab` or `.newCourse ABCD-12XX course-abcd` or `.newCourse AB-12XX course-ab` \
**Permissions:** Administrator \
**Note:**
- Will create a new role with the given course-name if it is the correct format.
- Will hoist the role to the appropriate position in the hierarchy with the greater course number placing higher.
- Will create a new channel under the appropriate category.
- Will position the channel to the appropriate position in the hierarchy relative to the other courses with the lower course number placing higher than the greater course numbers.
- If it is a course for a new category it will create the category and then place the channel inside.
- Will setup permissions not allowing members with the Not Registered role to read the messages while only allowing members with the specified course role to read messages.
- Cannot create a newCourse if there is an existing role for it.

**Purpose:** A shortcut which does not require the user to manually create a role and channel, worry about positioning, or permissions.
### New Course Reaction
**Command:** `.newCourseReaction [course-role] [course-description]` \
**Example:** `.newCourseReaction @ABCD-1234 abcd description` \
**Permissions:** Administrator \
**Note:**
- Given course-role must already exist.
- Will find the reaction role embedded message category associated with the course and create a reaction role for the new course with the next letter in the alphabet.
- Will edit the course description so that the new course's description is listed, and will be placed in the correct order relative to the other courses with the lower course number being listed higher.
- Will not execute if 26 letters already exist on the category's reaction role message.
- Will not execute if the given course already has a reaction role on the given message.

**Purpose:** A shortcut which does not require the user to manually create a reaction role for the course by giving specific information about channel, message_id, reaction and then manually edit another HuskyBot message for the course-description.
### New Course Complete
**Command:** `.newCourseComplete [course-role] [channel-description], [course-description]` \
**Example:** `.newCourseComplete ABCD-1234 abcd channel, abcd description` \
**Permissions:** Administrator \
**Note:** Must have a comma to separate the channel description and course description. (All other specifics pertaining to `.newCourse` and `.newCourseReaction`) \
**Purpose:** An all-in-one shortcut allowing the user to automate all the task of creating a new course carrying out the specifics of `.newCourse` followed by `.newCourseReaction`.

## Twitch
### Add Twitch
**Command:** `.addTwitch [twitch_username] [member_name]` \
**Example:** `.addTwitch HuskyStreams @HuskyBot#0821` or `.addTwitch RocketLeague` \
**Permissions:** Administrator \
**Purpose:** Adds a Twitch user to track for when their streams go live. A message will be sent in the #twitch when one of these members goes live. If a discord member name is sent, their tag will show as a field in the embedded message. \

### Remove Twitch
**Command:** `.removeTwitch [twitch_username]` \
**Example:** `.removeTwitch HuskyStreams` \
**Permissions:** Administrator \
**Purpose:** Removes a Twitch user from being traked for when their streams go live. \

### List Twitch
**Command:** `.listTwitch` \
**Example:** `.listTwitch` \
**Permissions:** Administrator \
**Purpose:** Lists all the Twitch members currently being tracked. \
