![HuksyBot Banner](https://i.imgur.com/7obLnAa.png)
A multi-function Discord Bot made specifically for the NU (Northeastern) Server

# Getting Started
 
 1. Clone this repo, e.g
     ```sh
     git@github.com:VishalRamesh50/Husky-Bot.git
     ```
 2. Install all dependencies:
    ```sh
    pip install -r requirements.txt
    ```
 3. Go to https://discordapp.com/developers to create an application and generate a `TOKEN` for a Bot account.
    - Click the New Application Button.
    - Give a name.
    - Go the the Bot section.
    - Select the "Add bot" button.
    - Find your `TOKEN` from the Bot section.
 4. Copy the `.env.example` file and rename to `.env`
     -  Open the `.env` file and replace the `TOKEN` with your unique `TOKEN`. Do not expose this anywhere!
 5. [Create a mongoDB cluster](https://docs.atlas.mongodb.com/tutorial/create-new-cluster/) for reaction role related functionality.
 6. Place the database username and password in the `.env` file.
 7. Run the application using
     ```sh
     python src/main.py
     ```

 *Note: This bot was intended to be specifically for the NU Discord Server. There may be features that will not work in any other server.*

# Features
- [Welcome Message](docs/DOCUMENTATION.md#welcome-message) 🎉
- [Automatic Member Registration Detection & Handling](docs/DOCUMENTATION.md#auto-member-registration-detection-and-handling) ✅
- [Reminder](docs/DOCUMENTATION.md#reminder) ⏲
- [Northeastern University Locations Hours](docs/DOCUMENTATION.md#hours) 🕒
- [Northeastern University Locations Open](docs/DOCUMENTATION.md#open) 🕒
- [Northeastern Univeristy Ice-Cream Flavors](docs/DOCUMENTATION.md#ice-cream) 🍦
- [Determines day for any given date](docs/DOCUMENTATION.md#day-date) 🗓
- [Music Bot Functionality](docs/DOCUMENTATION.md#music) 🎶
- [Moderation](docs/DOCUMENTATION.md#moderation) 🔍
- [Miscellaneous](docs/DOCUMENTATION.md#miscellaneous) ➕
- [Reaction Roles](docs/DOCUMENTATION.md#reaction-roles) 👍
- [Course Registration](docs/DOCUMENTATION.md#course-registration) 📚
- [Course Creation Shortcuts](docs/DOCUMENTATION.md#course-creation-shortcuts) 🚀
- [Activity](docs/DOCUMENTATION.md#activity) 🎮
- [Stats](docs/DOCUMENTATION.md#stats) 📊

# Documentation
Check out the documentation [here](docs/DOCUMENTATION.md)
