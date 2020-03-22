from discord.ext.commands.errors import CheckFailure
from typing import Optional


class InvalidChannel(CheckFailure):
    """Exception raised when the command invoker did not invoke in the
    required channel.

    This inherits from :exc:`CheckFailure`

    Attributes
    -----------
    missing_channel: `str`
        The name of the required channel which the command was not invoked in.
    """

    def __init__(self, missing_channel: Optional[str] = None, *args):
        if missing_channel is None:
            missing_channel = "a channel not in this guild."

        self.missing_channel = missing_channel

        message = f"This command must be invoked in {missing_channel}."
        super().__init__(message, *args)
