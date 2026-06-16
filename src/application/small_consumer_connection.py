"""Contains function to calculate the small consumer connection power."""

from __future__ import annotations

import math

from src.domain.connection_power import SmallConsumerCategory, SmallConsumerConnectionTypes


def calculate_small_consumer_connection(small_consumer_connection: str) -> int | float:
    """Calculates the small consumer connection power from the connection string.

    Args:
        small_consumer_connection: The small consumer connection string.
    """
    nr_of_phases = int(small_consumer_connection.split(" x ")[0])
    ampere = int(small_consumer_connection.split(" x ")[1].rstrip("A"))
    if nr_of_phases == 1:
        return int(nr_of_phases * ampere * 230 / 1000)
    return round(math.sqrt(nr_of_phases) * ampere * 400 / 1000, 2)


def small_consumer_connection_ranges() -> list[SmallConsumerCategory]:
    """Returns the minimum and maximum connection powers for each small consumer connection category."""
    connection_types = list(SmallConsumerConnectionTypes)
    return [
        SmallConsumerCategory(
            connection_type=SmallConsumerConnectionTypes.ONE_TIMES_SIX_AMPERE,
            min_connection_power=0,
            max_connection_power=calculate_small_consumer_connection(
                SmallConsumerConnectionTypes.ONE_TIMES_SIX_AMPERE.value
            ),
        )
    ] + [
        SmallConsumerCategory(
            connection_type=connection_types[small_consumer_type],
            min_connection_power=calculate_small_consumer_connection(connection_types[small_consumer_type - 1].value),
            max_connection_power=calculate_small_consumer_connection(connection_types[small_consumer_type].value),
        )
        for small_consumer_type in range(1, len(connection_types))
    ]
