import logging
from typing import TYPE_CHECKING, Literal, override

import discord
from discord.ext import commands

from biochemie_bot.bot import BiochemieBot

if TYPE_CHECKING:
    from discord.app_commands.models import AppCommand


class Developer(commands.Cog):
    """Includes various developer-only commands."""

    def __init__(self, bot: BiochemieBot) -> None:
        self.bot: BiochemieBot = bot
        self.logger: logging.Logger = logging.getLogger(__name__)

    @override
    async def cog_check(self, ctx: commands.Context[BiochemieBot]) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def shutdown(self, ctx: commands.Context[BiochemieBot]) -> None:
        """Shuts the bot down."""
        await ctx.send("Attempting to shut down cleanly...")
        self.logger.info("Shutdown: Manual")

        await self.bot.close()

    @commands.command()
    async def load(
        self,
        ctx: commands.Context[BiochemieBot],
        *,
        extension: str = commands.parameter(
            description="The extension to load",
        ),
    ) -> None:
        """Load the specified extension."""
        try:
            await self.bot.load_extension(f"biochemie_bot.cogs.{extension}")
        except commands.ExtensionError as error:
            await ctx.message.reply(f"{error.__class__.__name__}: {error}")
        else:
            await ctx.send(f"Extension `{extension}` has been loaded.")

    @commands.command()
    async def unload(
        self,
        ctx: commands.Context[BiochemieBot],
        *,
        extension: str = commands.parameter(
            description="The extension to unload",
        ),
    ) -> None:
        """Unload the specified extension."""
        try:
            await self.bot.unload_extension(f"biochemie_bot.cogs.{extension}")
        except commands.ExtensionError as error:
            await ctx.message.reply(f"{error.__class__.__name__}: {error}")
        else:
            await ctx.send(f"Extension `{extension}` has been unloaded.")

    @commands.command()
    async def reload(
        self,
        ctx: commands.Context[BiochemieBot],
        *,
        extension: str = commands.parameter(
            default=None,
            description="The extension to reload, reloads all if nothing is specified",
        ),
    ) -> None:
        """Reload the specified extension, reload everything if no extension is specified."""
        if extension:
            try:
                await self.bot.reload_extension(f"biochemie_bot.cogs.{extension}")
            except commands.ExtensionError as error:
                await ctx.message.reply(f"{error.__class__.__name__}: {error}")
            else:
                await ctx.send(f"Extension `{extension}` has been reloaded.")
        else:
            for ext in list(self.bot.extensions):
                try:
                    await self.bot.reload_extension(ext)
                except commands.ExtensionError as error:
                    await ctx.message.reply(f"{error.__class__.__name__}: {error}")

            await ctx.send("Reloaded all extensions.")

    @commands.command()
    async def extensions(self, ctx: commands.Context[BiochemieBot]) -> None:
        """Show all the loaded extensions."""
        await ctx.send(
            "The loaded extensions are: "
            f"{', '.join(ext.split('.')[-1] for ext in list(self.bot.extensions))}."
        )

    @commands.command()
    @commands.guild_only()
    async def sync(
        self,
        ctx: commands.Context[BiochemieBot],
        guilds: commands.Greedy[discord.Object] = commands.parameter(  # noqa: B008
            default=None, description="Guild IDs to sync, separated by space"
        ),
        spec: Literal["~", "*", "^"] | None = commands.parameter(
            default=None,
            description="Sync guild (~), copy and sync (*), clear and sync (^)",
        ),
    ) -> None:
        """Sync slash commands, syncs globally if no arguments are provided.

        Source: https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html
        """
        if guilds:
            count = 0
            for guild in guilds:
                try:
                    await self.bot.tree.sync(guild=guild)
                except discord.HTTPException:
                    pass
                else:
                    count += 1

            await ctx.send(f"Synced slash commands in {count}/{len(guilds)} guilds.")
            return

        match spec:
            case "~":
                synced: list[AppCommand] = await self.bot.tree.sync(guild=ctx.guild)

                await ctx.message.reply(
                    f"Synced {len(synced)} slash commands (groups) to the current guild."
                )
            case "*":
                if ctx.guild is None:
                    await ctx.message.reply("Failed to sync, ctx.guild is None.")
                    return

                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await self.bot.tree.sync(guild=ctx.guild)

                await ctx.message.reply(
                    f"Copied and synced {len(synced)} slash commands (groups) "
                    "to the current guild."
                )
            case "^":
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)

                await ctx.message.reply(
                    "Cleared guild slash commands and synced them with the global slash commands."
                )
            case _:
                synced = await self.bot.tree.sync()

                await ctx.message.reply(f"Synced {len(synced)} slash command (groups) globally.")


async def setup(bot: BiochemieBot) -> None:
    """Add Developer cog."""
    await bot.add_cog(Developer(bot))
