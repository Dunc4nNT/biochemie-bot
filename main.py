import asyncio

import discord

from biochemie_bot.bot import BiochemieBot
from config import bot_token, command_prefix


async def run_bot(intents: discord.Intents, initial_extensions: list[str]) -> None:
    """Run the main bot loop, with the required intents."""
    async with BiochemieBot(
        command_prefix=command_prefix, intents=intents, initial_extensions=initial_extensions
    ) as bot:
        await bot.start(bot_token)


def main() -> None:  # noqa: D103
    discord.utils.setup_logging()

    intents: discord.Intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    initial_extensions: list[str] = [
        "biochemie_bot.cogs.developer",
        "biochemie_bot.cogs.informatic",
    ]

    asyncio.run(run_bot(intents, initial_extensions))


if __name__ == "__main__":
    main()
