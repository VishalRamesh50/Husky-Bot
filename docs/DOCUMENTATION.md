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
  - Graduate
  - Newly Admitted
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

## Reminder
**Command:** `.reminder [insert-reminder-here] in [number] [unit-of-time]` \
**Example:** `.reminder get laundry in 32 mins` \
**Permissions:** Everyone \
**Note:** "in" is a mandatory word that must exist between the reminder and the time. (Case-insensitive) \
**Unit of time possibilities:** second, seconds, secs, sec, s, minutes, mins, min, m, hour, hours, hr, hrs, h, day, days, d, week, weeks, w \
**Purpose:** Confirmation message will be sent and user will receive a DM in the specified duration of time.

## Hours
**Command:** `.hours [location], [day]` \
**Example:** `.hours stwest, monday` \
**Permissions:** Everyone \
**Note:** Day is optional. If no day is provided, the current day is used by default. \
A location can be multiple words and can be valid under multiple aliases.\
A comma __must__ be used to separate the location and day. (Case-insensitive) \
**Possible Days:** Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sun, Mon, Tues, Wed, Thurs, Fri, Sat, Tomorrow \
**Supported Locations (as of Mar 2019):** International Village, Stetson East, Stetson West, Outtakes, Argo Tea, Café 716, Café Crossing, Faculty Club, Kigo's Kitchen, The Market, Popeyes, Rebecca's, Starbucks, Subway, Sweet Tomatoes, The West End, UBurger, Za'tar, Qdoba, Amelia's Taqueria, Boston Shawarma, Cappy's, Chicken Lou's, College Convenience, CVS, Dominos, Resmail, Gyroscope, Panera Bread, Pho and I, Star Market, Symphony Market, University House of Pizza, Whole Foods, Wings Over, Wollaston's Market, Wollaston's Market West Village. \
**Purpose:** Says the hours of operation of select locations and determines whether it's OPEN or CLOSED. Specifies minutes left until closing/opening if less than 1 hour remaining.

## Ice Cream
**Command:** `.icecream monday` \
**Permissions:** Everyone \
**Note:** Day is optional. If no day is provided, the current day will be used by default. \
**Purpose:** Displays what the current ice cream flavors are available any day from the Northeastern Dining Halls.

## Day Date
**Command:** `.day [date]` \
**Permissions:** Everyone \
**Example:** `.day 9/1/2022` or `.day Sept 1 2022` \
**Note:** If year is not provided, current year is used by default. However, year is mandatory for MM/DD/YYYY format. Year must be less than 10000 \
**Date Formats:** MM/DD/YYYY, Month Day Year, Month Day \
**Purpose:** Determines the day of any given date

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

## Moderation
**Command(s):** `.clear [number]` \
**Example:** `.clear 20` \
**Permissions:** Manage Messages \
**Note:** Must be greater than 0. \
**Purpose:** Clears the last given number of messages.

## Miscellaneous
**Commands:** `.ping`, `.echo`, `.flip`, `.menu`, `.invite` \
**Ping:** Returns Pong! \
**Echo:** Repeats anything the user says after the given command. \
**Flip:** Flips a coin and says the result (Heads/Tails) \
**Menu:** Generates a link to Northeastern's menu. \
**Invite:** Generates an invite link to the NU Discord Server.

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

## Course Registration
### Toggling AutoDelete
**Command:** `.toggleAD` \
**Example:** `.toggleAD` \
**Permissions:** Administrator \
**Note:** Will toggle the auto-delete functionality of the course registration, switching from deleting Husky Bot's messages to not. \
**Purpose:** Allows for user to toggle off auto-delete when creating new messages via HuskyBot in `#course-registration` and then toggle it back on to avoid spam from other users.
### Toggle Courses
**Command:** `.choose [role-name]` \
**Example:** `.choose [CS-2500]` or `.choose [cs 2500]` or `.choose spring green` \
**Permissions:** Administrator & Everyone \
**Note:**
- Non-admin users can only use this command in `#course-registration`.
- Non-admin users can only toggle courses in `#course-registration`.
- Admins can toggle any role and do it anywhere.
- Role names are case-insensitive, spaces are allowed, and courses do not require a '-' even though it is in the name.

**Purpose:** Toggle `#course-registration` roles without having to search for their reactions in the large channel.
### New Semester
**Command:** `.newSemester` \
**Example:** `.newSemester` \
**Permissions:** Administrator \
**Note:** Will remove all courses from every member in the server. \
**Purpose:** To initiate a fresh restart for all members and avoid having old members in courses they are not currently taking.
### Clear Courses
**Command:** `.clearCourses [member]` \
**Example:** `.clearCourses @User123#1234` \
**Permissions:** Administrator \
**Note:** Will remove all courses from a member. \
**Purpose:** Allows for easy deletion of all course roles from a user for specific cases especially spam.
### Clear Reactions
**Command:** `.clearReactions [member]` \
**Example:** `.clearReactions @User123#1234` \
**Permissions:** Administrator \
**Note:** Will remove all reactions given by a member in the `#course-registration` channel. There is a short timeout every 5 reactions removed if they are tied to a reaction role which the user currently has. \
**Purpose:** Allows for easy removal of all reactions from a user in `#course-registration` for specific cases especially spam.
### New Course Reaction Embed Message
**Command:** `.newEmbed [embed-title], [image-url]` \
**Example:** `.newEmbed Add/Remove ABCD courses, https://imgur.com/PKev2zr.png` \
**Permissions:** Administrator \
**Note:** Will create a new embedded message with the given title and image. Will also send a course description stub message which can be modified to describe which reactions correspond to each course. \
**Purpose:** Allows user to create embedded messages in `#course-registration` to use as differentiable sections and reaction role messages.
### Edit Embedded Message Image
**Command:** `.editEmbedImage [message] [image-url]` \
**Example:** `.editEmbedImage 123456789876543210 https://imgur.com/7obLnAa.png` \
**Permissions:** Administrator \
**Note:** Will set the embedded message's image to be the provided url. \
**Purpose:** Allows user to update any previously sent embedded message's image without resending a new one. Allows for easy updates to update section images if a user decides a new one is needed.
### Edit Embedded Message Title
**Command:** `.editEmbedTitle [message] [title]` \
**Example:** `.editEmbedTitle 123456789876543210 New Title` \
**Permissions:** Administrator \
**Note:** Will set the embedded message's title to be the provided title. \
**Purpose:** Allows users to update any previously sent embedded message's title without resending a new one. Allows for easy updates to update section title if a user decides a new one is needed.
### Edit Course Content
**Command:** `.editCourseContent [message] [content]` \
**Example:** `.editCourseContent 123456789876543210 blah blah blah \n blah blah blah` \
**Permissions:** Administrator \
**Note:**
- Will edit any message sent by Husky Bot with the new content.
- This will **overwrite** the content, **not** add to it.
- Any newlines must be indicated by typing `\n`, `shift-enter` will be ignored as a newline.
- This will not edit the content of an embedded message.

**Purpose:** Allows users to update any course descriptions in `#course-registration` in the case there is new content they need to add or fix.

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

## Activity
### Playing
**Command:** `.playing [activity_name]` \
**Example:** `.playing spotify` \
**Permissions:** Everyone \
**Note:** Any activity containing the keyword will be selected (not an exact match). So `.playing league` would find both League of Legends and Rocket League, for example. \
**Purpose:** Allows for the user to find all the members in a server that is playing a certain activity.

## Stats
### Server Info
**Command:** `.serverinfo` \
**Example:** `.serverinfo` \
**Permissions:** Administrator \
**Note:** None \
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
- Number of user currently on mobile
- Number of user who made a New Account (<1 day old account) before joining the server
- Number of emojis
- Verification Level
- Number of Active Invites
- 2FA State

### Ordered List Members
**Command:** `.orderedListMembers [number of members] [outputType]` \
**Example:** `.orderedListMembers 30 mention` or `.orderedListMembers 50` or `.orderedListMembers`\
**Permissions:** Administrator \
**Note:**
- Will default to 10 members if no arguments are given.
- If there are less than 10 members, it will get all the members.
- Will default to showing nicknames if no output type is given.
- OutputTypes: nick/nickname (user's nickname or username if no nickname), name (user's username), mention (user mentioned)
- Includes bot accounts.

**Purpose:** Returns a list of members, in an embedded message by order of the date they joined the server. \

### Join Position
**Command:** `.joinNo [number]` \
**Example:** `.joinNo 50` \
**Permissions:** Administrator \
**Note:** Will send error messages to guide the user if the given number is not within the range of members in the server. Includes bot accounts. \
**Purpose:** Returns some info about a user who joined the server at the given number. \
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

### Member Info
**Command:** `.whois [member_name]` \
**Aliases:** `.whoam` \
**Example:** `.whois discordUser0000` or `.whoam I` or `.whois` \
**Permissions:** Administrator and Everyone \
**Note:**
- Admins can find info about any member.
- Non-admin members can use this command to find out information about themselves.
- Will default to the user who sent the command if no arguments are given or the letter "I" is given.-
- Will search for members with spaces, is case-insensitive, and will check if the argument is within another member name.

**Purpose:** Returns some info about a member in the server. \
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
