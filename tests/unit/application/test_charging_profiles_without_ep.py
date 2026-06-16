"""Unit tests for application.charging_profiles_without_ep using Arrange/Act/Assert (AAA).

Each test follows Arrange / Act / Assert and returns None.
"""

import math
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from src.application.charging_profiles_without_ep import ChargingProfilesWithoutEP, Vehicle
from src.domain.vehicle_info import VehicleType


def test_vehicle_calculate_max_capacity_correctly() -> None:
    """Arrange: One van, power usage 0.2 kWh/km and annual driven km 20000.

    Act: Calculate maximum battery capacity of the vehicle.
    Assert: Maximum battery capacity has expected type and value.
    """
    # Arrange
    mock_vehicle = Vehicle(
        vehicle_type=VehicleType.VAN,
        power_usage=0.2,
        annual_km=20000,
        arrival_time=datetime(year=2025, month=1, day=1, hour=8, tzinfo=ZoneInfo("Europe/Amsterdam")),
        departure_time=datetime(year=2025, month=1, day=1, hour=18, tzinfo=ZoneInfo("Europe/Amsterdam")),
    )

    # Act
    expected_max_capacity = 11

    # Assert
    assert isinstance(mock_vehicle.max_capacity, int)
    assert mock_vehicle.max_capacity == expected_max_capacity


def test_vehicle_update_charging_correctly() -> None:
    """Arrange: One van, power usage 0.2 kWh/km and annual driven km 20000.

    Act: Update state of charge of the vehicle.
    Assert: Updated state of charge matches expected.
    """
    # Arrange
    mock_vehicle = Vehicle(
        vehicle_type=VehicleType.VAN,
        power_usage=0.2,
        annual_km=20000,
        arrival_time=datetime(year=2025, month=1, day=1, hour=8, tzinfo=ZoneInfo("Europe/Amsterdam")),
        departure_time=datetime(year=2025, month=1, day=1, hour=18, tzinfo=ZoneInfo("Europe/Amsterdam")),
    )

    # Act and assert
    mock_vehicle.update_is_charging()
    assert isinstance(mock_vehicle.is_charging, bool)
    assert mock_vehicle.is_charging

    # Act and assert
    mock_vehicle.update_is_charging()
    assert isinstance(mock_vehicle.is_charging, bool)
    assert not mock_vehicle.is_charging


def test_datetime_rounded_to_nearest_quarter_without_overnight_within_arrival_and_departure_correctly(
    mock_init_single_vehicle_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
) -> None:
    """Arrange: Without overnight charging and datetime that is within the arrival and departure time.

    Act: Round the datetime to the nearest quarter.
    Assert: Datetime is returned and rounded to the correct quarter.
    """
    # Arrange

    # Mock datetime to be rounded to nearest quarter
    mock_datetime = datetime(year=2025, month=1, day=2, hour=8, minute=17, tzinfo=ZoneInfo("Europe/Amsterdam"))

    # Initialize mock ChargingProfilesWithoutEP class with mock values
    mock_init_single_vehicle_without_overnight_charging.overnight_time = 0

    # Act
    result = mock_init_single_vehicle_without_overnight_charging._round_to_nearest_quarter(  # noqa: SLF001
        t=mock_datetime,
        arrival_datetime_day_nr=mock_arrival_and_departure_time_without_overnight_charging[0],
        departure_datetime_day_nr=mock_arrival_and_departure_time_without_overnight_charging[1],
        arrival=True,
    )

    # Assert
    assert isinstance(result, datetime)
    assert result == datetime(year=2025, month=1, day=2, hour=8, minute=15, tzinfo=ZoneInfo("Europe/Amsterdam"))


def test_datetime_rounded_to_nearest_quarter_with_overnight_datetime_before_arrival_correctly(
    mock_init_single_vehicle_with_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_with_overnight_charging: tuple[datetime, datetime],
) -> None:
    """Arrange: With overnight charging and datetime that is before the arrival time.

    Act: Round the datetime to the nearest quarter.
    Assert: Datetime is returned and is rounded to the correct quarter.
    """
    # Arrange

    # Mock datetime to be rounded to nearest quarter
    mock_datetime = datetime(year=2025, month=1, day=1, hour=7, minute=47, tzinfo=ZoneInfo("Europe/Amsterdam"))

    # Initialize mock ChargingProfilesWithoutEP class with mock values
    mock_init_single_vehicle_with_overnight_charging.overnight_time = 36  # 8 hours x 4 quarters per hour

    # Act
    result = mock_init_single_vehicle_with_overnight_charging._round_to_nearest_quarter(  # noqa: SLF001
        t=mock_datetime,
        arrival_datetime_day_nr=mock_arrival_and_departure_time_with_overnight_charging[0],
        departure_datetime_day_nr=mock_arrival_and_departure_time_with_overnight_charging[1],
        arrival=True,
    )

    # Assert
    assert isinstance(result, datetime)
    assert result == datetime(year=2025, month=1, day=1, hour=8, tzinfo=ZoneInfo("Europe/Amsterdam"))


def test_datetime_rounded_to_nearest_quarter_without_overnight_datetime_in_previous_day_correctly(
    mock_init_single_vehicle_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
) -> None:
    """Arrange: Without overnight charging and datetime that is in previous day.

    Act: Round the datetime to the nearest quarter.
    Assert: Datetime is returned and is rounded to the correct quarter.
    """
    # Arrange

    # Mock datetime to be rounded to nearest quarter
    mock_datetime = datetime(year=2025, month=1, day=1, hour=23, minute=47, tzinfo=ZoneInfo("Europe/Amsterdam"))

    # Initialize mock ChargingProfilesWithoutEP class with mock values
    mock_init_single_vehicle_without_overnight_charging.overnight_time = 0

    # Act
    result = mock_init_single_vehicle_without_overnight_charging._round_to_nearest_quarter(  # noqa: SLF001
        t=mock_datetime,
        arrival_datetime_day_nr=mock_arrival_and_departure_time_without_overnight_charging[0],
        departure_datetime_day_nr=mock_arrival_and_departure_time_without_overnight_charging[1],
        arrival=True,
    )

    # Assert
    assert isinstance(result, datetime)
    assert result == datetime(year=2025, month=1, day=2, tzinfo=ZoneInfo("Europe/Amsterdam"))


def test_datetime_rounded_to_nearest_quarter_without_overnight_datetime_after_departure_time_correctly(
    mock_init_single_vehicle_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
) -> None:
    """Arrange: Without overnight charging and datetime that is after the departure time.

    Act: Round the datetime to the nearest quarter.
    Assert: Datetime is returned and is rounded to the correct quarter.
    """
    # Arrange

    # Mock datetime to be rounded to nearest quarter
    mock_datetime = datetime(year=2025, month=1, day=2, hour=18, minute=47, tzinfo=ZoneInfo("Europe/Amsterdam"))

    # Initialize mock ChargingProfilesWithoutEP class with mock values
    mock_init_single_vehicle_without_overnight_charging.overnight_time = 0

    # Act
    result = mock_init_single_vehicle_without_overnight_charging._round_to_nearest_quarter(  # noqa: SLF001
        t=mock_datetime,
        arrival_datetime_day_nr=mock_arrival_and_departure_time_without_overnight_charging[0],
        departure_datetime_day_nr=mock_arrival_and_departure_time_without_overnight_charging[1],
        arrival=True,
    )

    # Assert
    assert isinstance(result, datetime)
    assert result == mock_arrival_and_departure_time_without_overnight_charging[1]


def test_datetime_rounded_to_nearest_quarter_without_overnight_within_arrival_and_departure_next_hour_correctly(
    mock_init_single_vehicle_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
) -> None:
    """Arrange: Without overnight charging and datetime that is within the arrival and departure time.

    Act: Round the datetime to the nearest quarter.
    Assert: Datetime is returned and is rounded to the correct quarter.
    """
    # Arrange

    # Mock datetime to be rounded to nearest quarter
    mock_datetime = datetime(year=2025, month=1, day=2, hour=8, minute=55, tzinfo=ZoneInfo("Europe/Amsterdam"))

    # Initialize mock ChargingProfilesWithoutEP class with mock values
    mock_init_single_vehicle_without_overnight_charging.overnight_time = 0

    # Act
    result = mock_init_single_vehicle_without_overnight_charging._round_to_nearest_quarter(  # noqa: SLF001
        t=mock_datetime,
        arrival_datetime_day_nr=mock_arrival_and_departure_time_without_overnight_charging[0],
        departure_datetime_day_nr=mock_arrival_and_departure_time_without_overnight_charging[1],
        arrival=True,
    )

    # Assert
    assert isinstance(result, datetime)
    assert result == datetime(year=2025, month=1, day=2, hour=9, minute=0, tzinfo=ZoneInfo("Europe/Amsterdam"))


@pytest.mark.rng_location("src.application.charging_profiles_without_ep")
def test_stochastic_arrival_times_day_correctly(
    seed_default_rng,  # noqa: ANN001, ARG001
    mock_init_multiple_vehicles_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
    mock_stochastic_arrival_times: np.ndarray,
    mock_stochastic_departure_times: np.ndarray,
) -> None:
    """Arrange: First day of the year, without overnight charging and 9 vehicles.

    Act: Calculate stochastic arrival times.
    Assert: Stochastic arrival times are determined correctly.
    """
    # Arrange

    # Initialize arrival and departure datetimes and overnight time with mock values
    mock_init_multiple_vehicles_without_overnight_charging.arrival_datetime = (
        mock_arrival_and_departure_time_without_overnight_charging[0]
    )
    mock_init_multiple_vehicles_without_overnight_charging.departure_datetime = (
        mock_arrival_and_departure_time_without_overnight_charging[1]
    )
    mock_init_multiple_vehicles_without_overnight_charging.overnight_time = 0

    # Act
    result_arrival, result_departure = (
        mock_init_multiple_vehicles_without_overnight_charging._stochastic_arrival_and_departure_times_day(day_nr=0)  # noqa: SLF001
    )

    # Expected number of vehicles
    total_nr_of_vehicles = 9

    # Assert
    assert isinstance(result_arrival, np.ndarray)
    assert isinstance(result_departure, np.ndarray)
    assert len(result_arrival) == total_nr_of_vehicles
    assert len(result_departure) == total_nr_of_vehicles
    for i in range(len(result_arrival)):
        assert result_arrival[i] == mock_stochastic_arrival_times[i]
    for i in range(len(result_departure)):
        assert result_departure[i] == mock_stochastic_departure_times[i]


@patch(
    "src.application.charging_profiles_without_ep.ChargingProfilesWithoutEP._stochastic_arrival_and_departure_times_day"
)
def test_create_vehicles_day_correctly(
    mock_stoch_arrival_departure_times_function: MagicMock,
    mock_init_multiple_vehicles_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
    mock_stochastic_arrival_times: np.ndarray,
    mock_stochastic_departure_times: np.ndarray,
    mock_vehicles: list[Vehicle],
) -> None:
    """Arrange: First day of the year, without overnight charging and 9 vehicles.

    Act: Create a list with vehicles including correct information.
    Assert: List of vehicles includes correct information.
    """
    # Arrange

    # Initialize arrival and departure datetimes and overnight time with mock values
    mock_init_multiple_vehicles_without_overnight_charging.arrival_datetime = (
        mock_arrival_and_departure_time_without_overnight_charging[0]
    )
    mock_init_multiple_vehicles_without_overnight_charging.departure_datetime = (
        mock_arrival_and_departure_time_without_overnight_charging[1]
    )
    mock_init_multiple_vehicles_without_overnight_charging.overnight_time = 0

    # Expected stochastic arrival times for each vehicle
    mock_stoch_arrival_departure_times_function.return_value = (
        mock_stochastic_arrival_times,
        mock_stochastic_departure_times,
    )

    # Act
    result = mock_init_multiple_vehicles_without_overnight_charging._create_vehicles_day(day_nr=0)  # noqa: SLF001

    # Expected number of vehicles and list of vehicles
    total_nr_of_vehicles = 9

    # Assert
    assert isinstance(result, list)
    assert len(result) == total_nr_of_vehicles

    for i in range(len(result)):
        assert hasattr(result[i], "vehicle_type")
        assert result[i].vehicle_type == mock_vehicles[i].vehicle_type

        assert hasattr(result[i], "power_usage")
        assert result[i].power_usage == mock_vehicles[i].power_usage

        assert hasattr(result[i], "annual_km")
        assert result[i].annual_km == mock_vehicles[i].annual_km

        assert hasattr(result[i], "arrival_time")
        assert result[i].arrival_time == mock_vehicles[i].arrival_time

        assert hasattr(result[i], "departure_time")
        assert result[i].departure_time == mock_vehicles[i].departure_time

        assert hasattr(result[i], "current_capacity")
        assert result[i].current_capacity == mock_vehicles[i].current_capacity

        assert hasattr(result[i], "is_charging")
        assert result[i].is_charging == mock_vehicles[i].is_charging

        assert hasattr(result[i], "max_capacity")
        assert result[i].max_capacity == mock_vehicles[i].max_capacity


def test_update_active_charging_sessions_t_correctly(
    mock_init_multiple_vehicles_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
    mock_vehicles: list[Vehicle],
) -> None:
    """Arrange: First day of the year, without overnight charging and 9 vehicles.

    Act: Update active charging sessions.
    Assert: Active charging sessions are updated correctly.
    """
    # Arrange

    # Mock datetimes for first day of the year
    overnight_time = 0
    days = 1
    mock_datetimes = np.array(
        [
            mock_arrival_and_departure_time_without_overnight_charging[0].replace(hour=0) + timedelta(minutes=15 * t)
            for t in range(96 * days + overnight_time)
        ]
    )

    # Initialize vehicles, datetimes and active charging sessions with mock values
    mock_init_multiple_vehicles_without_overnight_charging.vehicles = mock_vehicles
    mock_init_multiple_vehicles_without_overnight_charging.datetimes = mock_datetimes
    mock_init_multiple_vehicles_without_overnight_charging.active_charging_sessions = np.zeros(
        96 * days + overnight_time, dtype=int
    )
    mock_init_multiple_vehicles_without_overnight_charging._update_active_charging_sessions_t(t=8 * 4)  # noqa: SLF001

    # Act
    result_active_charging_sessions = mock_init_multiple_vehicles_without_overnight_charging.active_charging_sessions[
        8 * 4
    ]

    # Expected number of charging sessions
    expected_active_charging_sessions = 5

    # Assert
    assert expected_active_charging_sessions == result_active_charging_sessions
    assert mock_vehicles[0].is_charging
    assert mock_vehicles[1].is_charging
    assert not mock_vehicles[2].is_charging
    assert mock_vehicles[3].is_charging
    assert mock_vehicles[4].is_charging
    assert not mock_vehicles[5].is_charging
    assert not mock_vehicles[6].is_charging
    assert not mock_vehicles[7].is_charging
    assert mock_vehicles[8].is_charging


def test_update_avg_charging_power_t_correctly(
    mock_init_multiple_vehicles_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
    mock_vehicles: list[Vehicle],
) -> None:
    """Arrange: First day of the year, without overnight charging and 9 vehicles.

    Act: Update average charging power.
    Assert: Average charging power is updated correctly.
    """
    # Arrange

    # Mock datetimes for first day of the year
    overnight_time = 0
    days = 1
    mock_datetimes = np.array(
        [
            mock_arrival_and_departure_time_without_overnight_charging[0].replace(hour=0) + timedelta(minutes=15 * t)
            for t in range(96 * days + overnight_time)
        ]
    )

    # Initialize vehicles and datetimes
    mock_init_multiple_vehicles_without_overnight_charging.vehicles = mock_vehicles
    mock_init_multiple_vehicles_without_overnight_charging.datetimes = mock_datetimes

    # Initialize active charging sessions, average charging power and remaining connection power with mock values
    mock_init_multiple_vehicles_without_overnight_charging.active_charging_sessions = np.zeros(
        96 * days + overnight_time, dtype=int
    )
    mock_init_multiple_vehicles_without_overnight_charging.active_charging_sessions[8 * 4] = 4
    mock_init_multiple_vehicles_without_overnight_charging.avg_charging_power = np.zeros(
        96 * days + overnight_time, dtype=float
    )
    mock_init_multiple_vehicles_without_overnight_charging.remaining_connection_power = np.array(
        [10] * len(mock_datetimes)
    )

    # Act
    mock_init_multiple_vehicles_without_overnight_charging._update_avg_charging_power_t(t=8 * 4)  # noqa: SLF001

    # Assert
    assert math.isclose(mock_init_multiple_vehicles_without_overnight_charging.avg_charging_power[8 * 4], 10 / 4)


def test_update_total_charging_power_t_correctly(
    mock_init_multiple_vehicles_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
    mock_vehicles_t_36: list[Vehicle],
) -> None:
    """Arrange: First day of the year, without overnight charging and 9 vehicles.

    Act: Update total charging power.
    Assert: Total charging power is updated correctly.
    """
    # Arrange

    # Mock datetimes for first day of the year
    overnight_time = 0
    days = 1
    mock_datetimes = np.array(
        [
            mock_arrival_and_departure_time_without_overnight_charging[0].replace(hour=0) + timedelta(minutes=15 * t)
            for t in range(96 * days + overnight_time)
        ]
    )

    # Initialize vehicles and datetimes
    mock_init_multiple_vehicles_without_overnight_charging.vehicles = mock_vehicles_t_36
    mock_init_multiple_vehicles_without_overnight_charging.datetimes = mock_datetimes

    # Initialize average charging power and total charging power with mock values
    mock_init_multiple_vehicles_without_overnight_charging.avg_charging_power = np.zeros(
        96 * days + overnight_time, dtype=float
    )
    mock_init_multiple_vehicles_without_overnight_charging.avg_charging_power[8 * 4] = 10 / 5
    mock_init_multiple_vehicles_without_overnight_charging.total_charging_power = np.zeros(
        96 * days + overnight_time, dtype=float
    )

    # Act
    mock_init_multiple_vehicles_without_overnight_charging._update_total_charging_power_t(t=8 * 4)  # noqa: SLF001

    expected_total_power = 10

    # Assert
    assert mock_init_multiple_vehicles_without_overnight_charging.total_charging_power[8 * 4] == expected_total_power
    assert mock_vehicles_t_36[0].current_capacity == 10 / 5 * 0.25
    assert not mock_vehicles_t_36[0].is_charging
    assert mock_vehicles_t_36[1].current_capacity == 10 / 5 * 0.25
    assert not mock_vehicles_t_36[1].is_charging
    assert mock_vehicles_t_36[2].current_capacity == 0
    assert not mock_vehicles_t_36[2].is_charging
    assert mock_vehicles_t_36[3].current_capacity == 10 / 5 * 0.25
    assert not mock_vehicles_t_36[3].is_charging
    assert mock_vehicles_t_36[4].current_capacity == 10 / 5 * 0.25 + 10 / 2 * 0.25
    assert not mock_vehicles_t_36[4].is_charging
    assert mock_vehicles_t_36[5].current_capacity == 0
    assert not mock_vehicles_t_36[5].is_charging
    assert mock_vehicles_t_36[6].current_capacity == 0
    assert not mock_vehicles_t_36[6].is_charging
    assert mock_vehicles_t_36[7].current_capacity == 0
    assert not mock_vehicles_t_36[7].is_charging
    assert mock_vehicles_t_36[8].current_capacity == 10 / 5 * 0.25 + 10 / 2 * 0.25
    assert not mock_vehicles_t_36[8].is_charging
