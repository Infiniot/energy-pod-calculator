"""Integration tests for application.charging_profiles_without_ep using Arrange/Act/Assert (AAA).

Each test follows Arrange / Act / Assert and returns None.
"""

import math
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import numpy as np

from src.application.charging_profiles_without_ep import ChargingProfilesWithoutEP, Vehicle


def test_schedule_charging_vehicles_day_correctly(
    mock_init_multiple_vehicles_without_overnight_charging: ChargingProfilesWithoutEP,
    mock_arrival_and_departure_time_without_overnight_charging: tuple[datetime, datetime],
    mock_vehicles: list[Vehicle],
    expected_active_charging_sessions: np.ndarray,
    expected_avg_charging_power: np.ndarray,
    expected_total_charging_power_schedule_charging_vehicles: np.ndarray,
    expected_vehicle_current_capacity: np.ndarray,
) -> None:
    """Arrange: Indices for first day of the year, without overnight charging and 9 vehicles.

    Act: Schedule charging for 9 vehicles for the first day of the year.
    Arrange: Charging for 9 vehicles is scheduled correctly.
    """
    # Arrange

    # Mock indices day
    mock_indices_day = np.array(list(range(96)))

    # Mock datetimes for first day of the year
    mock_datetimes = np.array(
        [
            mock_arrival_and_departure_time_without_overnight_charging[0].replace(hour=0) + timedelta(minutes=15 * t)
            for t in range(96)
        ]
    )

    mock_remaining_connection_power = np.array([45] * 96 * 365)

    # Initialize vehicles and datetimes
    mock_init_multiple_vehicles_without_overnight_charging.vehicles = mock_vehicles
    mock_init_multiple_vehicles_without_overnight_charging.datetimes = mock_datetimes
    mock_init_multiple_vehicles_without_overnight_charging.remaining_connection_power = mock_remaining_connection_power

    # Initialize average charging power and total charging power with mock values
    mock_init_multiple_vehicles_without_overnight_charging.active_charging_sessions = np.zeros(96, dtype=int)
    mock_init_multiple_vehicles_without_overnight_charging.avg_charging_power = np.zeros(96, dtype=float)
    mock_init_multiple_vehicles_without_overnight_charging.total_charging_power = np.zeros(96, dtype=float)

    # Act
    mock_init_multiple_vehicles_without_overnight_charging._schedule_charging_vehicles_day(  # noqa: SLF001
        indices_day=mock_indices_day
    )

    # Assert
    for t in mock_indices_day:
        assert (
            mock_init_multiple_vehicles_without_overnight_charging.active_charging_sessions[t]
            == expected_active_charging_sessions[t]
        )
        assert math.isclose(
            mock_init_multiple_vehicles_without_overnight_charging.avg_charging_power[t],
            expected_avg_charging_power[t],
        )
        assert math.isclose(
            round(mock_init_multiple_vehicles_without_overnight_charging.total_charging_power[t], 2),
            expected_total_charging_power_schedule_charging_vehicles[t],
        )

    for v in range(len(mock_vehicles)):
        assert math.isclose(
            mock_init_multiple_vehicles_without_overnight_charging.vehicles[v].current_capacity,
            expected_vehicle_current_capacity[v],
        )
        assert not mock_init_multiple_vehicles_without_overnight_charging.vehicles[v].is_charging


@patch("src.application.charging_profiles_without_ep.np.astype")
def test_calculate_charging_profiles_without_ep_correctly_without_overnight(
    stoch_times: MagicMock,
    mock_stoch_times: np.ndarray,
    mock_init_multiple_vehicles_without_overnight_charging: ChargingProfilesWithoutEP,
    expected_total_charging_power_year_without_ep_without_overnight: np.ndarray,
) -> None:
    """Arrange: Stochastic times are set to fixed values for each iteration.

    Act: Calculate charging profiles without overnight charging.
    Assert: Charging profiles without overnight charging are calculated correctly.
    """
    # Arrange
    stoch_times.return_value = mock_stoch_times
    expected_uncharged_power = 153759.9
    expected_vehicles_not_fully_charged = 2920

    # Act
    results_without_ep = mock_init_multiple_vehicles_without_overnight_charging.calculate_charging_profiles_without_ep()

    # Assert
    assert hasattr(results_without_ep, "charging_profiles")
    assert hasattr(results_without_ep, "uncharged_power")
    assert hasattr(results_without_ep, "vehicles_not_fully_charged")
    assert hasattr(results_without_ep, "worst_day_uncharged_power")
    assert hasattr(results_without_ep, "worst_day_vehicles")

    for t in range(365 * 96):
        assert math.isclose(
            results_without_ep.charging_profiles[t].power,
            expected_total_charging_power_year_without_ep_without_overnight[t],
        )

    assert math.isclose(expected_uncharged_power, np.sum(results_without_ep.uncharged_power))
    assert expected_vehicles_not_fully_charged == np.sum(results_without_ep.vehicles_not_fully_charged)
    assert results_without_ep.worst_day_uncharged_power == datetime(
        year=2026, month=1, day=1, tzinfo=ZoneInfo(key="Europe/Amsterdam")
    )
    assert results_without_ep.worst_day_vehicles == datetime(
        year=2026, month=1, day=1, tzinfo=ZoneInfo(key="Europe/Amsterdam")
    )


@patch("src.application.charging_profiles_without_ep.np.astype")
def test_calculate_charging_profiles_without_ep_correctly_with_overnight(
    stoch_times: MagicMock,
    mock_stoch_times: np.ndarray,
    mock_init_multiple_vehicles_with_overnight_charging: ChargingProfilesWithoutEP,
    expected_total_charging_power_year_with_overnight: np.ndarray,
) -> None:
    """Arrange: Stochastic times are set to fixed values for each iteration.

    Act: Calculate charging profiles with overnight charging.
    Assert: Charging profiles with overnight charging are calculated correctly.
    """
    # Arrange
    stoch_times.return_value = mock_stoch_times
    expected_uncharged_power = 105448.50
    expected_vehicles_not_fully_charged = 1095

    # Act
    results_without_ep = mock_init_multiple_vehicles_with_overnight_charging.calculate_charging_profiles_without_ep()

    # Assert
    assert hasattr(results_without_ep, "charging_profiles")
    assert hasattr(results_without_ep, "uncharged_power")
    assert hasattr(results_without_ep, "vehicles_not_fully_charged")
    assert hasattr(results_without_ep, "worst_day_uncharged_power")
    assert hasattr(results_without_ep, "worst_day_vehicles")

    for t in range(365 * 96):
        assert math.isclose(
            results_without_ep.charging_profiles[t].power, expected_total_charging_power_year_with_overnight[t]
        )

    assert math.isclose(expected_uncharged_power, np.sum(results_without_ep.uncharged_power))
    assert expected_vehicles_not_fully_charged == np.sum(results_without_ep.vehicles_not_fully_charged)
    assert results_without_ep.worst_day_uncharged_power == datetime(
        year=2026, month=1, day=1, tzinfo=ZoneInfo(key="Europe/Amsterdam")
    )
    assert results_without_ep.worst_day_vehicles == datetime(
        year=2026, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam")
    )
