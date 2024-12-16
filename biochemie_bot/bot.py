import logging
from datetime import datetime
from typing import override

import discord
from discord import app_commands
from discord.ext import commands


class BiochemieBot(commands.Bot):
    """Represents the Discord bot, which subclasses :class:`commands.Bot`."""

    user: discord.ClientUser
    app_info: discord.AppInfo  # type: ignore[reportUninitializedInstanceVariable]
    start_time: datetime | None = None
    log: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self, command_prefix: str, intents: discord.Intents, initial_extensions: list[str]
    ) -> None:
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.initial_extensions: list[str] = initial_extensions

    @override
    async def setup_hook(self) -> None:
        self.app_info = await self.application_info()
        self.tree.on_error = self.on_app_command_error

        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
            except commands.ExtensionError as error:
                self.log.exception("Failed to load extension: %s", extension, exc_info=error)

    async def on_ready(self) -> None:
        """When the bot just connected with the gateway, set start time if not already done."""
        if self.start_time is None:
            self.start_time = discord.utils.utcnow()

        self.log.info("Ready: %s (%s)", self.user, self.user.id)

    @override
    async def on_command_error(
        self, ctx: commands.Context["BiochemieBot"], error: commands.CommandError
    ) -> None:
        if ctx.command and ctx.command.has_error_handler():
            return

        if ctx.cog and ctx.cog.has_error_handler():
            return

        ignored_errors = (
            commands.CommandNotFound,
            commands.CheckFailure,
            commands.CheckAnyFailure,
        )

        if isinstance(error, ignored_errors):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.message.reply(f"Command `{ctx.command}` has been disabled.")
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.message.reply(
                    f"Command `{ctx.command}` cannot be used in private messages."
                )
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(f"Command `{ctx.command}` failed to process, {error}")
        else:
            await ctx.message.reply(f"Something went wrong while processing `{ctx.command}`.")

            self.log.error("Ignoring exception in command %s", ctx.command, exc_info=error)

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Handle any errors bubbled up to app command error handler.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction which caused the error.
        error : app_commands.AppCommandError
            The actual error.
        """
        if isinstance(error, app_commands.CommandNotFound):
            await interaction.response.send_message(
                "This command is temporarily disabled.", ephemeral=True
            )
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)
        elif isinstance(error, app_commands.MissingRole | app_commands.MissingAnyRole):
            await interaction.response.send_message(
                "You are missing the required role(s) to run this command",
                ephemeral=True,
            )
        elif isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "A check has failed, possible causes for this could be:\n"
                "- You do not have the required role(s)\n"
                "- You do not have the required permissions\n"
                "- The command is disabled\n"
                "- You are banned from using commands",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Something went wrong while processing this interaction.",
                ephemeral=True,
            )

            self.log.error("Ignoring exception in interaction.", exc_info=error)
