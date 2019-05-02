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

Once a member has all 3, the "Not Registered" Role will be removed. If not all 3 are present the "Not Registered" Role will be assigned.

## Reminder
**Command:** `.reminder [insert-reminder-here] in [number] [unit-of-time]` \
**Example:** `.reminder get laundry in 32 mins` \
**Note:** "in" is a mandatory word that must exist between the reminder and the time. (Case-insensitive) \
**Unit of time possibilities:** second, seconds, secs, sec, s, minutes, mins, min, m, hour, hours, hr, hrs, h, day, days, d, week, weeks, w \
**Purpose:** Confirmation message will be sent and user will receive a DM in the specified duration of time.

## Hours
**Command:** `.hours [location], [day]` \
**Example:** `.hours stwest, monday` \
**Note:** Day is optional. If no day is provided, the current day is used by default. \
A location can be multiple words and can be valid under multiple aliases.\
A comma __must__ be used to separate the location and day. (Case-insensitive) \
**Possible Days:** Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sun, Mon, Tues, Wed, Thurs, Fri, Sat, Tomorrow \
**Supported Locations (as of Mar 2019):** International Village, Stetson East, Stetson West, Outtakes, Argo Tea, Café 716, Café Crossing, Faculty Club, Kigo's Kitchen, The Market, Popeyes, Rebecca's, Starbucks, Subway, Sweet Tomatoes, The West End, UBurger, Za'tar, Qdoba, Amelia's Taqueria, Boston Shawarma, Cappy's, Chicken Lou's, College Convenience, CVS, Dominos, Resmail, Gyroscope, Panera Bread, Pho and I, Star Market, Symphony Market, University House of Pizza, Whole Foods, Wings Over, Wollaston's Market, Wollaston's Market West Village. \
**Purpose:** Says the hours of operation of select locations and determines whether it's OPEN or CLOSED. Specifies minutes left until closing/opening if less than 1 hour remaining.

## Ice Cream
**Command:** `.icecream monday` \
**Note:** Day is optional. If no day is provided, the current day will be used by default. \
**Purpose:** Displays what the current ice cream flavors are available any day from the Northeastern Dining Halls.

## Day Date
**Command:** `.day [date]` \
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
**Note:** Only members with the "Admin" role can use Moderation commands. \
**Purpose:** Clears the last given number of messages. Must be greater than 0.

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
**Note:**
- Given **channel** can be in the form of a mentioned channel or just the name.
- Given **message id** must be a valid message id and a number.
- Given **emoji** must be a valid emoji in the correct form (Ex: `:thumbs_up:`).
- Given **role** can be in the form of a mentioned role or just the name.

**Purpose:** Allows for the user to select a specific message that users can react to with a chosen emoji to get assigned a role and unreact to remove the role.
### Fetching Reaction Role Information
**Command:** `.fetchrr [message_id]` \
**Example:** `.fetchrr 123456789876543210` \
**Note:** Given message id must be a valid message id and a number. \
**Purpose:** Fetches all the keys, reaction, and roles corresponding to each reaction role for the given message id.
### Removing a Reaction Role
**Command:** `.removerr [key]` \
**Example:** `.removerr F0xUOpxMv` \
**Note:** Given key must be a valid key. Each reaction role is assigned a unique key and can be found in the embedded message upon creation of the reaction role or by using the `.fetchrr` command. \
**Purpose:** Allows for the user to delete any reaction role by giving the unique key.
### Removing All Reaction Roles for Message
**Command:** `.removeallrr [message_id]` \
**Example:** `.removeallrr 123456789876543210` \
**Note:** Given message id must be a valid message id and a number. \
**Purpose:** Allows for the user to delete all reaction roles from a given message at once.

## Activity
### Playing
**Command:** `.playing [activity_name]` \
**Example:** `.playing spotify` \
**Note:** Any activity containing the keyword will be selected (not an exact match). So `.playing league` would find both League of Legends and Rocket League, for example. \
**Purpose:** Allows for the user to find all the members in a server that is playing a certain activity.
