"""Custom charging window error."""


class ChargingWindowError(Exception):
    """Custom exception class for charging window error."""

    def __init__(self) -> None:
        """Initialize error with specified message and log error."""
        message = "Failed to schedule charging sessions: vehicle cannot be fully charged within time window."
        super().__init__(message)
        self.message = message
