# Biochemie Bot

Small bot for biochemie.

## Prerequisites

The following software is required to run the bot.

- [Python v3.13 or higher](https://www.python.org/downloads/)
- [Poetry v1.8.4 or higher](https://python-poetry.org/docs/#installation)
- [Discord Bot](https://discord.com/developers/applications) - [more info](https://discordpy.readthedocs.io/en/stable/discord.html)

## Installation

1. Create a venv using `py -m venv .venv`.
2. Activate venv with poetry using `poetry shell`.
3. Install all the dependencies and bot by running `poetry install`.
4. Copy the `config.py.example` file to `config.py` using `cp config.py.example config.py`.
5. Add you bot token to `bot_token` inside `config.py`.

## Config

```py
bot_token: str = "" # your discord bot token.
command_prefix: str = "-" # your bot prefix for non-slash commands.
repository_link = "https://github.com/Dunc4nNT/biochemie-bot" # link to the bot repository.
```

## Running the Bot

Run the `main.py` file by typing `poetry run py main.py`.
