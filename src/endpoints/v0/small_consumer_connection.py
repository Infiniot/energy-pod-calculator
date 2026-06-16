"""The router containing the endpoint for calculating the small consumer connection capacity."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.small_consumer_connection import calculate_small_consumer_connection

small_consumer_connection_router = APIRouter(prefix="/small_consumer_connection", tags=["small consumer connection"])


@small_consumer_connection_router.get("/")
def get_small_consumer_connection(small_consumer_connection: str) -> float:
    """Retrieves the power of the current connection for the given parameters.

    Args:
        small_consumer_connection: The current connection to the grid.
    """
    return calculate_small_consumer_connection(small_consumer_connection)
