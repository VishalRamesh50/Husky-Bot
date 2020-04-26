![HuksyBot Banner](https://i.imgur.com/7obLnAa.png)
A multi-function Discord Bot made specifically for the NU (Northeastern) Server

# Features

- [Welcome Message](docs/DOCUMENTATION.md#welcome-message) 🎉
- [Automatic Member Registration Detection & Handling](docs/DOCUMENTATION.md#auto-member-registration-detection-and-handling) ✅

## Admin/Mod Only Commands

- [Aoun](docs/DOCUMENTATION.md#aoun) 🎓
- [Clear](docs/DOCUMENTATION.md#clear) ⌫
- [Course Registration](docs/DOCUMENTATION.md#course-registration) 📚
- [Reaction](docs/DOCUMENTATION.md#reaction) 👍
- [Twitch](docs/DOCUMENTATION.md#twitch) 📺

## Public Commands

- [Activity](docs/DOCUMENTATION.md#activity) 🎮
- [Day Date](docs/DOCUMENTATION.md#day-date) 🗓
- [Hours](docs/DOCUMENTATION.md#hours) 🕒
- [Ice Cream](docs/DOCUMENTATION.md#ice-cream) 🍦
- [Miscellaneous](docs/DOCUMENTATION.md#miscellaneous) ➕
- [Open](docs/DOCUMENTATION.md#open) 🕒
- [Reminder](docs/DOCUMENTATION.md#reminder) ⏲
- [Stats](docs/DOCUMENTATION.md#stats) 📊
- [Suggest](docs/DOCUMENTATION.md#suggest) 📬

# Getting Started

1.  Clone this repo, e.g
    ```sh
    git clone git@github.com:VishalRamesh50/Husky-Bot.git
    ```
2.  Install all dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3.  Copy the `.env.example` file and rename to `.env`
    ```sh
    cp .env.example .env
    ```
4.  Go to https://discordapp.com/developers to create an application and generate a `TOKEN` for a Bot account.
    - Click the New Application Button.
    - Give a name.
    - Go the the Bot section.
    - Select the "Add bot" button.
    - Find your `TOKEN` from the Bot section.
    - Open the `.env` file and replace the `TOKEN` with your unique `TOKEN`. Do not expose this anywhere!
    - Your application will not run without this.
5.  [Create a mongoDB cluster](https://docs.atlas.mongodb.com/tutorial/create-new-cluster/)
    - This is required for the reaction role, april fools, and twitch modules.
    - When in the Clusters section of mongoDB Atlas, click the "Connect" button.
    - Choose "Connect Your Application".
    - Select Python as the driver and Version 3.6 or later.
    - Copy the connection string, replace your username and password in it, and replace the `DB_CONNECTION_URL` with this in the `.env` file.
6.  Register a Twitch application at https://dev.twitch.tv/console.
    - This is required for the twitch module.
    - Click the "Register Your Application" button.
    - Get the Client-ID from your appilication and replace the `TWITCH_CLIENT_ID` with it in the `.env` file.
7.  Run the application using
    ```sh
    python src/main.py
    ```

_Note: This bot was intended to be specifically for the NU Discord Server. There may be features that will not work in any other server._

# Documentation

Check out the documentation [here](docs/DOCUMENTATION.md)
