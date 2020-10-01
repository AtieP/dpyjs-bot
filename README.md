# Discord.py & Discord.js Discord Bot
This bot is made specifically for the [Discord.py & Discord.js community.](https://dpyjs.xyz).

# Setting up the bot
- Install PostgreSQL, and create a database called `dpyjs` with owner `dpyjs`
- Create the tables specified in the `setup-sql.sql` file
- Install Python 3.8+
- Install Pipenv (`pip install pipenv`)
- Install all the packages and dev packages (`pipenv install`, `pipenv install --dev`)
- Create a new file named `config.yml` but with the same contents as `config-default.yml`,
  but changing some of the keys


# Running the bot
- Run `pipenv shell`
- Set up these four enviroment variables: `DPYJS_DATABASE_URL`, `DPYJS_BOT_TOKEN`, `DPYJS_SNEKBOX_URL` and `DPYJS_BAD_WORDS_REGEX`.
  - `DPYJS_BOT_TOKEN` is the bot's token.  
  - `DPYJS_DATABASE_URL` is the database URL, if you made a database named `dpyjs` with
  owner `dpyjs` that is running in `localhost` (127.0.0.1), `postgresql://dpyjs@localhost/dpyjs` is okay.  
  - `DPYJS_SNEKBOX_URL` is required for the public eval command to work. If you want to set up Snekbox, please
  [visit this page](https://github.com/python-discord/snekbox).  
  - `DPYJS_BAD_WORDS_REGEX` is a regular expression with bad words.
- Run `pipenv run start`


# Contributing to the bot
- If you propose a code change, please, lint the bot. This is done by running `flake8`.
