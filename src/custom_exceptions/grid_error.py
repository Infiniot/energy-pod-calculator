"""Custom grid tariff calculation errors."""


class ZipCodeError(Exception):
    """Custom exception class for zip code error."""

    def __init__(self) -> None:
        """Initialize error with specified message and log error."""
        message = "Invalid ZIP code: failed to map ZIP code to DSO."
        super().__init__(message)
        self.message = message


class ConnectionCapacityError(Exception):
    """Custom exception class for connection capacity error."""

    def __init__(self, connection: str) -> None:
        """Initialize error with specified message and log error."""
        message = f"Connection capacity '{connection}' is invalid."
        super().__init__(message)
        self.message = message


class GridTariffDSORangeError(Exception):
    """Custom exception class for when the connection capacity is out of range for the DSO."""

    def __init__(self, message: str = "Capacity is out of the possible capacity range for the DSO.") -> None:
        """Initialize error with specified message and log error."""
        super().__init__(message)
        self.message = message
