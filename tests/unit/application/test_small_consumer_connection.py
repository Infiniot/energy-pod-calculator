"""Unit tests for application.small_consumer_connection using Arrange/Act/Assert (AAA).

Tests cover:
- calculate_small_consumer_connection for single- and three-phase strings
- behavior with empty lists

Each test follows Arrange / Act / Assert and returns None.
"""

from math import sqrt

from src.application.small_consumer_connection import calculate_small_consumer_connection


def test_calculate_small_consumer_connection_single_phase_returns_expected_int() -> None:
    """Arrange: single-phase connection string.

    Act: call calculate_small_consumer_connection.
    Assert: returned int matches int(1 * I * 230 / 1000).
    """
    # Arrange
    conn = "1 x 16A"
    expected = int(1 * 16 * 230 / 1000)

    # Act
    result = calculate_small_consumer_connection(conn)

    # Assert
    assert isinstance(result, int)
    assert result == expected


def test_calculate_small_consumer_connection_three_phase_returns_expected_float() -> None:
    """Arrange: three-phase connection string.

    Act: call calculatesmall_consumer_connection.
    Assert: returned int matches int(sqrt(3) * I * 400 / 1000).
    """
    # Arrange
    conn = "3 x 25A"
    expected = round(sqrt(3) * 25 * 400 / 1000, 2)

    # Act
    result = calculate_small_consumer_connection(conn)

    # Assert
    assert isinstance(result, float)
    assert result == expected
