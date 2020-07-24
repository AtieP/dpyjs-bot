[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Website](https://img.shields.io/badge/website-visit-brightgreen)](https://dpyjs.xyz/)

# dpyjs-bot
Bot for the "Discord.py &amp; Discord.js" community. This bot is supposed to be only run there, but you can also host it on your own server!

# Installation
In order to run this bot, you must install:
- [CPython](https://www.python.org/downloads/). Make sure to also install Pip.
- [PostgreSQL](https://postgresql.org).
- [Pipenv](https://pipenv.pypa.io/en/latest/). You can only install this once you installed CPython and Pip.

# Preparation
Before you run the bot from the first time, you must:
- Run `pipenv install` on the main bot directory to install the necessary packages and to also setup a virtual enviroment.
- Create a PostgreSQL with the name of `dpyjs-bot-db` and run the `setup-db.sql` file to setup all tables. Make sure to grant permissions to yourself!
- Create a replica of our server and edit the `config.json` file accordingly.
- Create folder `temp` on the main bot directory.

# Run
1. Set up the three enviroment variables: `DPYJS_DB_USER` (the Postgres username), `DPYJS_DB_PASSWORD` (the Postgres user password) and `DPYJS_BOT_TOKEN` (the bot token).
- On Windows:
```batch
set DPYJS_DB_USER=postgres_user_name
set DPYJS_DB_PASSWORD=postgres_user_password
set DPYJS_BOT_TOKEN=bot_token
```
- On Linux:
```bash
export DPYJS_DB_USER=postgres_user_name
export DPYJS_DB_PASSWORD=postgres_user_password
export DPYJS_BOT_TOKEN=bot_token
```
And then run on the main bot directory `pipenv run start`. You're done!

# Contribution guide
Thanks for willing to contribute to this bot!

## Style guide for issues
Just provide helpful information like a complete description, screenshots...

## Style guide for pull requests
To get started, create a fork of this repository. These are the style guidelines you must follow:
- **Follow PEP 8.**
- Test the bot before.
- Include a nice description of your changes.
