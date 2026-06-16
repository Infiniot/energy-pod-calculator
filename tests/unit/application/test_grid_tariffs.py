"""Unit tests for application.grid_tariffs using Arrange/Act/Assert (AAA).

Tests cover:
- get_dso retrieving the DSO based on zip code
- map_connection_to_range mapping connection category to power range
- calculate_grid_tariff_small calculating small consumer grid tariffs, including error handling for invalid connections
- calculate_grid_tariff_large calculating large consumer grid tariffs, including error handling for out of range
  connection capacities

Each test follows the AAA pattern and returns None.
"""

from datetime import UTC, datetime

import pytest

from src.application.grid_tariffs import (
    calculate_grid_tariff_large,
    calculate_grid_tariff_small,
    get_dso,
    map_connection_to_range,
)
from src.custom_exceptions.grid_error import (
    ConnectionCapacityError,
    GridTariffDSORangeError,
    ZipCodeError,
)
from src.domain.baseload_profile import BaseloadProfile
from src.domain.grid_tariff import GridTariffDTOLargeConsumer, GridTariffDTOSmallConsumer


def test_get_dso_returns_correct_value() -> None:
    """Arrange: Prepare a valid zip code.

    Act: Call get_dso.
    Assert: Returned value has correct value and type.
    """
    # Arrange
    valid_zip_code = "1111AA"
    expected_dso = "Liander"

    # Act
    result = get_dso(valid_zip_code)

    # Assert
    assert isinstance(result, str)
    assert result == expected_dso


def test_get_dso_raises_error() -> None:
    """Arrange: Prepare a non existing zip code.

    Act: Call get_dso.
    Assert: ZipCodeError is raised.
    """
    # Arrange
    non_existing_zip_code = "1234AB"

    # Act / assert
    with pytest.raises(ZipCodeError):
        get_dso(non_existing_zip_code)


def test_map_connection_power_to_range_returns_correct_value() -> None:
    """Arrange: Prepare a mock connection capacity.

    Act: Call map_connection_to_range.
    Assert: Returned has correct value and type.
    """
    # Arrange
    mock_connection = "1 x 40A"
    expected_range = "≤ 3x25A"

    # Act
    result = map_connection_to_range(mock_connection)

    # Assert
    assert isinstance(result, str)
    assert result == expected_range


def test_map_connection_power_to_range_raises_error() -> None:
    """Arrange: Prepare a non existing mock connection.

    Act: Call map_connection_to_range.
    Assert: ConnectionCapacityError is raised.
    """
    # Arrange
    mock_connection = "3 x 6A"

    # Act / assert
    with pytest.raises(ConnectionCapacityError):
        map_connection_to_range(mock_connection)


def test_calculate_grid_tariff_small_returns_correct_value() -> None:
    """Arrange: Prepare a valid GridTariffDTOSmallConsumer input.

    Act: Call calculate_grid_tariff_small.
    Assert: Returned value has correct value and type.
    """
    # Arrange
    grid_tariff_input = GridTariffDTOSmallConsumer(
        zip_code="1111AA",
        connection_category="1 x 40A",
    )
    expected_tariff = 455.74

    # Act
    result = calculate_grid_tariff_small(grid_tariff_input)

    # Assert
    assert isinstance(result, float)
    assert result == expected_tariff


def test_calculate_grid_tariff_large_returns_correct_value() -> None:
    """Arrange: Prepare a valid GridTariffDTOLargeConsumer input.

    Act: Call calculate_grid_tariff_large.
    Assert: Returned value has correct value and type.
    """
    # Arrange
    grid_tariff_input = GridTariffDTOLargeConsumer(
        zip_code="1111AA",
        contract_capacity=0.2,
        connection_capacity=0.3,
        baseload=[BaseloadProfile(datetime=datetime(2024, 1, 1, 0, 0, tzinfo=UTC), power=2.0)],
    )
    expected_tariff = 14354.01

    # Act
    result = calculate_grid_tariff_large(grid_tariff_input)

    # Assert
    assert isinstance(result, float)
    assert result == expected_tariff


def test_calculate_grid_tariff_large_raises_error() -> None:
    """Arrange: Prepare a GridTariffDTOLargeConsumer input with out of range connection capacity.

    Act: Call calculate_grid_tariff_large.
    Assert: GridTariffDSORangeError is raised.
    """
    # Arrange
    grid_tariff_input = GridTariffDTOLargeConsumer(
        zip_code="7471AA",
        contract_capacity=6,
        connection_capacity=7,
        baseload=[BaseloadProfile(datetime=datetime(2024, 1, 1, 0, 0, tzinfo=UTC), power=2.0)],
    )

    # Act / assert
    with pytest.raises(GridTariffDSORangeError):
        calculate_grid_tariff_large(grid_tariff_input)
