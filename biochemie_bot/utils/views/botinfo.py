import platform
import shutil
import sys
from datetime import UTC, datetime
from typing import TYPE_CHECKING, override

import discord
import psutil
from discord import app_commands

from biochemie_bot import version_info
from biochemie_bot.bot import BiochemieBot
from biochemie_bot.utils.utils import format_timedelta
from biochemie_bot.utils.views.base import BaseView
from config import repository_link

if TYPE_CHECKING:
    from datetime import timedelta


class BotInfoView(BaseView):
    """View used in the `/bot info` command."""

    def __init__(
        self,
        author: discord.User | discord.Member,
        interaction: discord.Interaction,
        bot: BiochemieBot,
        cooldown: float = 0,
        timeout: float | None = 180,
    ) -> None:
        super().__init__(
            author=author,
            original_interaction=interaction,
            cooldown=cooldown,
            timeout=timeout,
        )
        self.bot: BiochemieBot = bot

        self.add_item(BotInfoSelect())
        self.add_item(
            discord.ui.Button(
                label="Invite",
                url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8",
                style=discord.ButtonStyle.link,
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Repository",
                url=repository_link,
                style=discord.ButtonStyle.link,
            )
        )


class BotInfoSelect(discord.ui.Select):
    """Select menu used in the `/bot info` command."""

    def __init__(self) -> None:
        options: list[discord.SelectOption] = [
            discord.SelectOption(
                label="Client Information",
                emoji="🤖",
                description="Information about the bot.",
                value="0",
            ),
            discord.SelectOption(
                label="System Information",
                emoji="🖥️",
                description="Information about the system the bot is running on.",
                value="1",
            ),
        ]
        super().__init__(
            min_values=1,
            max_values=1,
            options=options,
            placeholder="Select other information",
        )

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if not self.view:
            msg = "BotInfoSelect is not used inside of a view"
            raise AttributeError(msg)

        match self.values[0]:
            case "0":
                embed = bot_info_embed(self.view.bot)
                await interaction.response.edit_message(embed=embed)
            case "1":
                embed = system_info_embed(self.view.bot)
                await interaction.response.edit_message(embed=embed)
            case _:
                pass


def bot_info_embed(bot: BiochemieBot) -> discord.Embed:
    """Embed with bot data to send when the `/bot info` command is used.

    Parameters
    ----------
    bot : BiochemieBot
        The bot instance.

    Returns
    -------
    discord.Embed
        The formatted embed with information added.
    """
    embed = discord.Embed(
        title="Bot Information",
        description=f"[Source Code]({repository_link})",
        colour=0x3F3368,
        timestamp=discord.utils.utcnow(),
    )

    td: str = "N/A"
    if bot.start_time is not None:
        uptime: timedelta = discord.utils.utcnow() - bot.start_time
        td = format_timedelta(uptime)

    process = psutil.Process()
    memory: float = round(process.memory_full_info().rss / 2**20, 1)

    embed.add_field(
        name="Information",
        value=f"```yml\n"
        f"Uptime: {td}\n"
        f"Latency: {round(bot.latency * 1000)} ms\n"
        f"RAM in use: {memory} MiB```",
        inline=False,
    )

    embed.add_field(
        name="Bot Stats",
        value=f"```yml\n"
        f"Guilds: {len(bot.guilds)}\n"
        f"Members: {len(list(bot.get_all_members()))}\n"
        f"Channels: {len(list(bot.get_all_channels()))}```",
        inline=False,
    )

    command_counter = {
        "cogs": len(bot.cogs),
        "prefix_commands": len(bot.commands),
        "slash_groups": 0,
        "slash_commands": 0,
    }

    slash_commands = bot.tree.get_commands()
    for cmd in slash_commands:
        if isinstance(cmd, app_commands.Group):
            command_counter["slash_groups"] += 1
            command_counter["slash_commands"] += len(cmd.commands)
        else:
            command_counter["slash_commands"] += 1

    total_command_count = command_counter["prefix_commands"] + command_counter["slash_commands"]

    embed.add_field(
        name="Commands",
        value=f"```yml\n"
        f"Command Cogs: {command_counter['cogs']}\n"
        f"Prefix Commands: {command_counter['prefix_commands']}\n"
        f"Slash Groups: {command_counter['slash_groups']}\n"
        f"Slash Commands: {command_counter['slash_commands']}\n"
        f"Total Commands: {total_command_count}```",
    )

    py_version = sys.version_info
    dpy_version = discord.version_info

    embed.add_field(
        name="Version Info",
        value=f"```yml\n"
        f"BiochemieBot: {version_info.major}.{version_info.minor}.{version_info.micro}\n"
        f"Python: {py_version.major}.{py_version.minor}.{py_version.micro}\n"
        f"Discord.py: {dpy_version.major}.{dpy_version.minor}.{dpy_version.micro}\n"
        "```",
        inline=False,
    )

    set_info_embed_footer(bot, embed)

    return embed


def system_info_embed(bot: BiochemieBot) -> discord.Embed:
    """Embed with system data to send when the `/bot info` command is used.

    Parameters
    ----------
    bot : BiochemieBot
        The bot instance.

    Returns
    -------
    discord.Embed
        The formatted embed with information added.
    """
    embed = discord.Embed(
        title="System Information",
        colour=0x3F3368,
        timestamp=discord.utils.utcnow(),
    )

    uname = platform.uname()
    boot_time = datetime.fromtimestamp(psutil.boot_time(), UTC)
    system_uptime = discord.utils.utcnow() - boot_time
    system_uptime = format_timedelta(system_uptime)

    embed.add_field(
        name="System",
        value=f"```yml\nOS: {uname.system}\nMachine: {uname.machine}\nUptime: {system_uptime}```",
        inline=False,
    )

    embed.add_field(
        name="CPU",
        value=f"```yml\n"
        f"Name: {platform.processor()}\n"
        f"Physical Cores: {psutil.cpu_count(logical=False)}/{psutil.cpu_count(logical=True)}\n"
        f"Usage: {psutil.cpu_percent()}%```",
        inline=False,
    )

    vmem = psutil.virtual_memory()

    embed.add_field(
        name="Memory",
        value=f"```yml\n"
        f"Total Memory: {round(vmem.total / 2**30, 1)} GiB\n"
        f"Used Memory: {round(vmem.used / 2**30, 1)} GiB ({vmem.percent}%)\n"
        f"Free Memory: {round(vmem.free / 2**30, 1)} GiB```",
    )

    disk_io = psutil.disk_io_counters()
    read = round(disk_io.read_bytes / 2**30, 1) if disk_io else "?"
    write = round(disk_io.write_bytes / 2**30, 1) if disk_io else "?"
    total, used, _free = shutil.disk_usage("/")
    total_gib = total / 2**30
    used_gib = used / 2**30

    embed.add_field(
        name="Disk",
        value=f"```yml\n"
        f"Size: {round(total_gib, 1)} GiB\n"
        f"Used: {round(used_gib, 1)} GiB ({round(used_gib / total_gib * 100, 1)}%)\n\n"
        f"Read: {read} GiB\n"
        f"Write: {write} GiB```",
    )

    net_io = psutil.net_io_counters()

    embed.add_field(
        name="Network",
        value=f"```yml\n"
        f"Bytes Sent: {round(net_io.bytes_sent / 2**30, 1)} GiB\n"
        f"Bytes Received: {round(net_io.bytes_recv / 2**30, 1)} GiB\n"
        f"Packets Sent: {net_io.packets_sent:,}\n"
        f"Packets Received: {net_io.packets_recv:,}```",
        inline=False,
    )

    set_info_embed_footer(bot, embed)

    return embed


def set_info_embed_footer(bot: BiochemieBot, embed: discord.Embed) -> None:
    """Set footer information for the `/bot info` command."""
    embed.set_footer(
        text=f"Created by {bot.app_info.owner.name}",
        icon_url=bot.app_info.owner.display_avatar.url,
    )
