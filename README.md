# DatSimonBot
Versatile telegram bot

## Functionality
### School Schedules
Allows you to manage your and your friends' school schedule and makes planning of meetings easier.

#### This means you can:
- Create new schedules
- Add lessons to them
- Check the current status of your friends (If they are busy or not right now)
- See where your next lesson is
- Display all of the existing plans as an image
- Copy schedules and move them to other groups or to a private conversation

#### Additional functionality:
- Schedule ownership system (Will prevent others from messing up your plan)
- Support for lessons taking place every other week

#### Commands:
Instead of 'schedule' the word 'plan' is used here for convenience.
`/create_plan` - Create a new lesson plan
`/delete_plan` - Delete a lesson plan
`/get_plan` - Get a lesson plan
`/plan` - Get a lesson plan
`/get_plans` - Get all lesson plans
`/delete_all` - Delete all lesson plans
`/add_lesson` - Add a lesson to a plan
`/remove_lesson` - Remove a lesson from a plan
`/edit_lesson` - Edit a lesson in a plan
`/clear_day` - Clear all lessons for a day
`/clear_all` - Clear all lessons for a plan
`/edit_plan` - Edit a plan name
`/status` - Get status of all students in the group
`/where_next` - Send room you have lesson in next
`/where_now` - Send room you have your lesson in now
`/join_plan` - Join a lesson plan
`/leave_plan` - Leave a lesson plan
`/get_students` - Get all students in a plan
`/copy_plan` - Copy plan
`/paste_plan` - Paste plan
`/get_owners` - Get all plan owners (Admins only)
`/transfer_plan_ownership` - Transfer plan ownership
`/week_info` - Returns if week is odd or even
`/get_next_train` - Returns the next train

### Daily Images
You can schedule this bot to send a random image from defined set of images every day at 6 am.

#### This means you can:
- Create image sets within a group
- Add images to this set
- Get a random image from created sets
- Schedule daily image posting

#### Commands:
`/create_set` - Create a new set for daily images
`/delete_set` - Delete a set for daily images
`/daily_image` - Toggle daily image for given set
`/cancel_daily_image` - Cancel daily image
`/submit_image` - Submit an image to a set
`/random_image` - Send a random image from a set

### Other Functions
Functions made for fun or other smaller features

#### Wordle patterns
Currently supports only one pattern

🟨⬛️⬛️⬛️🟨
🟨🟩🟩⬛️⬛️
🟨⬛️⬛️⬛️⬛️
🟨⬛️⬛️⬛️🟨
🟨⬛️🟨⬛️🟨

`/wordle_among_us` command will allow you to achieve this pattern in different color variants in the game of Wordle by presenting you the necessary words.

It uses wordle api to get the current answer if no argument is given.

Some variants will not be achievable every day because of inability to provide valid words to get this color pattern.

#### 'Silly cipher'
Custom made cipher made to confuse your friends. It can be easily typed on gboard.

There's two ways to use this cipher:
    - using inline `@DatSimonBot silly <text>`
    - using command `/silly_cipher (reply to a message)`

Both of those allow deciphering and encoding the messages.

#### Utility functions
Functions making the usage of other commands easier. Or overall QOL functionality.

##### Commands:
`who_am_i` - Get user id
`whoami` - Same as above
`who_are_you` - Get the sender id (Need to reply to a message)
`stt` - Speech to text, allows to convert any voice messages to text for free

##### Emote actions:
🫰 - If you reply to a message with this emote, the message will dissapear spectacularly (This requires being an admin to prevent abuse)
📊 - Will create a yes/no poll from a message that you responded to
➕ - The bot will repeat the message that you responded to

### Help
If you are unsure of how to use any of the avaible commands there's a built in documentation avaible with the use of `/help`

By itself `/help` will display all of the avaible commands and their descriptions

By providing a command name after it you will be presented with info describing the use of the command and all of the possible functionality. For example `/help paste_plan` will return:

```
Paste a plan from the user data and save it in the group data.

Usage: /paste_plan or /paste_plan <plan_name>

Command parameters
-----------
plan_name : text (optional)
Name of the plan, if not provided, will use the previous name
```

You can also use `/help help` if you are confused about what does something mean in the provided description

### Possible Future Functionalities

Currently I am working on:
    - Simplifying the code
    - Extenting the koleo trains functionality
    - Extending the API functionality
    - Allowing the bot to 'hot reload' in order to speed up the development
 
