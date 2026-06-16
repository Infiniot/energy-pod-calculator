"""Unit tests for utils.time_frame using Arrange / Act / Assert (AAA).

Each test follows AAA, includes a docstring and returns None.
"""

from src.utils.time_frame import calculate_indices_arrival_departure_time


def test_calculate_indices_arrival_departure_time_without_overnight() -> None:
    """Arrange: Prepare mock arrival and departure time without overnight charging.

    Act: Call calculate_indices_arrival_departure_time.
    Assert: Returned has correct type and values.
    """
    # Arrange
    mock_arrival_time = "08:15"
    mock_departure_time = "18:30"

    # Act
    result = calculate_indices_arrival_departure_time(mock_arrival_time, mock_departure_time)
    expected_t_arr_ind = 33
    expected_t_dep_ind = 74

    # Assert
    assert isinstance(result, tuple)
    assert isinstance(result[0], int)
    assert isinstance(result[1], int)
    assert result[0] == expected_t_arr_ind
    assert result[1] == expected_t_dep_ind


def test_calculate_indices_arrival_departure_time_with_overnight() -> None:
    """Arrange: Prepare mock arrival and departure time with overnight charging.

    Act: Call calculate_indices_arrival_departure_time.
    Assert: Returned has correct type and values.
    """
    # Arrange
    mock_arrival_time = "18:00"
    mock_departure_time = "08:45"

    # Act
    result = calculate_indices_arrival_departure_time(mock_arrival_time, mock_departure_time)
    expected_t_arr_ind = 72
    expected_t_dep_ind = 131

    # Assert
    assert isinstance(result, tuple)
    assert isinstance(result[0], int)
    assert isinstance(result[1], int)
    assert result[0] == expected_t_arr_ind
    assert result[1] == expected_t_dep_ind
