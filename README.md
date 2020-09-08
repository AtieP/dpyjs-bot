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
- Set up these two enviroment variables: `DPYJS_DATABASE_URL` and `DPYJS_BOT_TOKEN`.
  `DPYJS_DATABASE_URL` is the database URL, if you made a database named `dpyjs` with
  owner `dpyjs` that is running in `localhost` (127.0.0.1), `postgresql://dpyjs@localhost/dpyjs` is okay.
- Run `pipenv run start`


# Contributing to the bot
- If you propose a code change, please, lint the bot. This is done by running `flake8`.
