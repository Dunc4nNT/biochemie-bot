import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from biochemie_bot.bot import BiochemieBot
from biochemie_bot.utils import utils
from biochemie_bot.utils.views.botinfo import BotInfoView, bot_info_embed

if TYPE_CHECKING:
    from datetime import timedelta


class Informatic(commands.Cog):
    """Includes various informational commands."""

    def __init__(self, bot: BiochemieBot) -> None:
        self.bot: BiochemieBot = bot
        self.logger: logging.Logger = logging.getLogger(__name__)

    infobot_group: app_commands.Group = app_commands.Group(
        name="bot", description="Informatic bot-related commands."
    )

    @infobot_group.command()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Show the latency between discord and the bot."""
        await interaction.response.send_message(
            f"`{round(self.bot.latency * 1000)}ms` latency to the Discord API."
        )

    @infobot_group.command()
    async def uptime(self, interaction: discord.Interaction) -> None:
        """Show the time passed since the bot started."""
        if self.bot.start_time is None:
            return

        uptime: timedelta = discord.utils.utcnow() - self.bot.start_time
        td: str = utils.format_timedelta(uptime)

        await interaction.response.send_message(
            f"Up since {discord.utils.format_dt(self.bot.start_time, 'f')}, which is {td} ago."
        )

    @infobot_group.command(name="info")
    async def botinfo(self, interaction: discord.Interaction) -> None:
        """Display some info about the bot."""
        embed = bot_info_embed(self.bot)

        await interaction.response.send_message(
            embed=embed,
            view=BotInfoView(
                author=interaction.user,
                interaction=interaction,
                bot=self.bot,
            ),
        )


async def setup(bot: BiochemieBot) -> None:
    """Add Informatic cog."""
    await bot.add_cog(Informatic(bot))
