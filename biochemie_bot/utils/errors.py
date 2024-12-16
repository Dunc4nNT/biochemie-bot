from discord.ext import commands


class ButtonOnCooldown(commands.CommandError):
    """Raise when a button is on cooldown."""

    def __init__(self, time_left: float) -> None:
        self.time_left = time_left
