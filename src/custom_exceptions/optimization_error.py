"""Custom optimization error."""


class OptimizationError(Exception):
    """Custom exception class for optimization error."""

    def __init__(self) -> None:
        """Initialize error with specified message and log error."""
        message = "Failed: Problem was not solvable."
        super().__init__(message)
        self.message = message
