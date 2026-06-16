"""Unit tests for src.application.optimization.EnergyPodOptimization using Arrange/Act/Assert (AAA).

Tests cover:
- map_times behaviour
- convert_input keys and battery parsing
- calculate_optimization successful solve path (patching solver + value)
- calculate_optimization failure path (solver returns non-success)
"""

from datetime import datetime, timedelta, timezone
from unittest import mock
from unittest.mock import patch
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from src.application.optimization import EnergyPodOptimization
from src.config import days_in_current_year
from src.custom_exceptions.optimization_error import OptimizationError
from src.domain.baseload_profile import BaseloadProfile
from src.domain.energy_dto import EnergyDTOSmallConsumer
from src.domain.vehicle_info import VehicleInfoDTO, VehicleType, VehicleTypeInfo, VehicleTypeInfoDTO


@pytest.fixture
def valid_energy_pod_input() -> EnergyDTOSmallConsumer:
    """Arrange: provide a minimal EnergyPodDTO object with required attributes."""
    return EnergyDTOSmallConsumer(
        vehicle_info=VehicleInfoDTO(
            vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.2, annual_km=2000),
            boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.5, annual_km=5000),
            semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1.0, annual_km=10000),
        ),
        arrival_time="08:00",
        departure_time="18:00",
        baseload=[BaseloadProfile(datetime=datetime(2025, 1, 1, tzinfo=ZoneInfo("Europe/Amsterdam")), power=0.0)]
        * 96
        * 365,
        zip_code="1111AA",
        connection_category="3 x 25A",
        battery_capacity=100,
        charge_point_power=200,
    )


@pytest.fixture
def seed_default_rng(request: pytest.FixtureRequest):  # noqa: ANN201
    """Fixture: default generator to always get the same sequence of random numbers."""
    seeded_rng = np.random.default_rng(seed=0)
    mock_location = request.node.get_closest_marker("rng_location").args[0]
    with mock.patch(f"{mock_location}.np.random.default_rng") as mocked:
        mocked.return_value = seeded_rng
        yield


def make_datetimes(n: int) -> list[datetime]:
    """Helper: create n datetimes spaced 15 minutes starting at 2025-01-01T00:00Z."""
    start = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    return [start + timedelta(minutes=15 * i) for i in range(n)]


@pytest.mark.rng_location("src.application.optimization")
def test_map_times_single_day_returns_expected_indices(
    seed_default_rng,  # noqa: ANN001, ARG001
) -> None:
    """Arrange: create optimizer for 1 day with one vehicle of each type.

    Act: call map_times for a single day.
    Assert: returned arrival/departure lists have expected length and values.
    """
    # Arrange
    datetimes = make_datetimes(96 * (days_in_current_year + 1))
    energy_prices = [1.0] * 96 * (days_in_current_year + 1)
    baseload = [0.0] * 96 * (days_in_current_year + 1)
    contract_power = [17.0] * 96 * (days_in_current_year + 1)
    mock_vehicle_info = [
        VehicleTypeInfo(
            vehicle_type=VehicleType.VAN,
            nr_of_vehicles=1,
            power_usage=0.2,
            annual_km=2000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.BOXTRUCK,
            nr_of_vehicles=1,
            power_usage=0.5,
            annual_km=5000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.SEMITRAILERTRUCK,
            nr_of_vehicles=1,
            power_usage=1.0,
            annual_km=10000,
        ),
    ]
    opt = EnergyPodOptimization(
        arrival_time="08:00",
        departure_time="18:00",
        vehicle_info=mock_vehicle_info,
        contract_connection_power=contract_power,
        max_connection_power=17,
        charge_point_power=200,
        battery_size=100,
        datetimes=datetimes,
        energy_prices=energy_prices,
        baseload=baseload,
    )
    expected_length = 3
    # Act
    t_arr, t_dep, overnight, _ = opt._map_times(days=1)  # noqa: SLF001

    # Assert
    # We provided 1 vehicle per type => total 3 arrival indices for the day
    assert isinstance(t_arr, dict)
    assert isinstance(t_dep, dict)
    assert [t_arr[x][0] for x in t_arr] == [29, 35, 31]
    assert [t_dep[x][0] for x in t_dep] == [71, 70, 73]
    assert list(t_arr) == [VehicleType.VAN, VehicleType.BOXTRUCK, VehicleType.SEMITRAILERTRUCK]
    assert list(t_dep) == [VehicleType.VAN, VehicleType.BOXTRUCK, VehicleType.SEMITRAILERTRUCK]
    assert isinstance(overnight, bool)
    assert len(t_arr) == expected_length
    assert len(t_dep) == expected_length
    assert overnight is False


@pytest.mark.rng_location("src.application.optimization")
def test_convert_input_contains_expected_keys(
    seed_default_rng,  # noqa: ANN001, ARG001
) -> None:
    """Arrange: build optimizer and call convert_input.

    Act: request conversion for 1 interval day.
    Assert: returned dict contains expected keys and battery parsed as int.
    """
    # Arrange
    datetimes = make_datetimes(96 * (days_in_current_year + 1))
    energy_prices = [1.0] * 96 * (days_in_current_year + 1)
    baseload = [0.0] * 96 * (days_in_current_year + 1)
    contract_power = [17.0] * 96 * (days_in_current_year + 1)
    mock_vehicle_info = [
        VehicleTypeInfo(
            vehicle_type=VehicleType.VAN,
            nr_of_vehicles=1,
            power_usage=0.2,
            annual_km=2000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.BOXTRUCK,
            nr_of_vehicles=1,
            power_usage=0.5,
            annual_km=5000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.SEMITRAILERTRUCK,
            nr_of_vehicles=1,
            power_usage=1.0,
            annual_km=10000,
        ),
    ]
    opt = EnergyPodOptimization(
        arrival_time="08:00",
        departure_time="18:00",
        vehicle_info=mock_vehicle_info,
        contract_connection_power=contract_power,
        max_connection_power=17,
        charge_point_power=200,
        battery_size=100,
        datetimes=datetimes,
        energy_prices=energy_prices,
        baseload=baseload,
    )

    # Act
    converted = opt._convert_input(days_in_current_year)  # noqa: SLF001

    # Assert
    expected_keys = {"vehicle_demands", "t_arr", "t_dep", "P_min", "P_max", "overnight"}
    assert expected_keys.issubset(set(converted.keys()))
    assert [converted["t_arr"][x][0] for x in converted["t_arr"]] == [29, 31, 33]
    assert [converted["t_dep"][x][0] for x in converted["t_dep"]] == [72, 71, 72]


def test_calculate_optimization_solver_failure_raises_optimization_error() -> None:
    """Arrange: patch solver to return a non-success code.

    Act / Assert: calculate_optimization should raise OptimizationError.
    """
    # Arrange
    datetimes = make_datetimes(96 * (days_in_current_year + 1))
    energy_prices = [1.0] * 96 * (days_in_current_year + 1)
    baseload = [0.0] * 96 * (days_in_current_year + 1)
    contract_power = [17.0] * 96 * (days_in_current_year + 1)
    mock_vehicle_info = [
        VehicleTypeInfo(
            vehicle_type=VehicleType.VAN,
            nr_of_vehicles=1,
            power_usage=0.2,
            annual_km=2000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.BOXTRUCK,
            nr_of_vehicles=1,
            power_usage=0.5,
            annual_km=5000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.SEMITRAILERTRUCK,
            nr_of_vehicles=1,
            power_usage=1.0,
            annual_km=10000,
        ),
    ]
    opt = EnergyPodOptimization(
        arrival_time="08:00",
        departure_time="18:00",
        vehicle_info=mock_vehicle_info,
        contract_connection_power=contract_power,
        max_connection_power=17,
        charge_point_power=200,
        battery_size=100,
        datetimes=datetimes,
        energy_prices=energy_prices,
        baseload=baseload,
    )

    # Patch solver to simulate failure
    with patch.object(opt.prob, "solve", return_value=0), pytest.raises(OptimizationError):
        # Act / Assert
        opt.calculate_optimization_results()


def test_vehicle_demands_calculates_correctly(valid_energy_pod_input: EnergyDTOSmallConsumer) -> None:
    """Arrange: create optimizer for 1 day with one vehicle of each type.

    Act / Assert: E_Vdem should match expected values for energy demand.
    """
    # Arrange
    datetimes = make_datetimes(96 * (days_in_current_year + 1))
    energy_prices = [1.0] * 96 * (days_in_current_year + 1)
    baseload = [0.0] * 96 * (days_in_current_year + 1)
    contract_power = [17.0] * 96 * (days_in_current_year + 1)
    mock_vehicle_info = [
        VehicleTypeInfo(
            vehicle_type=VehicleType.VAN,
            nr_of_vehicles=1,
            power_usage=0.2,
            annual_km=2000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.BOXTRUCK,
            nr_of_vehicles=1,
            power_usage=0.5,
            annual_km=5000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.SEMITRAILERTRUCK,
            nr_of_vehicles=1,
            power_usage=1.0,
            annual_km=10000,
        ),
    ]
    opt = EnergyPodOptimization(
        arrival_time="08:00",
        departure_time="18:00",
        vehicle_info=mock_vehicle_info,
        contract_connection_power=contract_power,
        max_connection_power=17,
        charge_point_power=200,
        battery_size=100,
        datetimes=datetimes,
        energy_prices=energy_prices,
        baseload=baseload,
    )

    # Act / Assert
    expected_demands = [
        round(
            valid_energy_pod_input.vehicle_info.vans.power_usage
            * valid_energy_pod_input.vehicle_info.vans.annual_km
            / 365
        ),
        round(
            valid_energy_pod_input.vehicle_info.boxtrucks.power_usage
            * valid_energy_pod_input.vehicle_info.boxtrucks.annual_km
            / 365
        ),
        round(
            valid_energy_pod_input.vehicle_info.semitrailertrucks.power_usage
            * valid_energy_pod_input.vehicle_info.semitrailertrucks.annual_km
            / 365
        ),
    ]
    assert opt.E_Vdem == sum(expected_demands)


def test_calculates_penalties_correctly() -> None:
    """Arrange: create an optimizer with low contract power.

    Act / Assert: The optimizer should return a solution with penalties.
    """
    # Arrange
    datetimes = make_datetimes(96 * (days_in_current_year + 1))
    energy_prices = [1.0] * 96 * (days_in_current_year + 1)
    baseload = [0.0] * 96 * (days_in_current_year + 1)
    contract_power = [1.0] * 96 * (days_in_current_year + 1)
    mock_vehicle_info = [
        VehicleTypeInfo(
            vehicle_type=VehicleType.SEMITRAILERTRUCK,
            nr_of_vehicles=1,
            power_usage=100.0,
            annual_km=365,
        ),
    ]
    opt = EnergyPodOptimization(
        arrival_time="08:00",
        departure_time="15:00",
        vehicle_info=mock_vehicle_info,
        contract_connection_power=contract_power,
        max_connection_power=400,
        charge_point_power=200,
        battery_size=0,
        datetimes=datetimes,
        energy_prices=energy_prices,
        baseload=baseload,
    )
    optimization_results = opt.calculate_optimization_results()

    assert np.any([opt.P_pen[ppen].value() for ppen in opt.P_pen])
    assert optimization_results.total_costs_capacity_exceedances > 0


def test_optimization_calculates_correct_power() -> None:
    """Arrange: create optimizer for 1 day with specified connection power.

    Act: calculate optimization and extract resulting battery charge/discharge values.
    Assert: calculated power should match vehicle energy demand and battery power balance should be correct.
    """
    # Arrange
    datetimes = make_datetimes(96 * (days_in_current_year + 1))
    energy_prices = [1.0] * 96 * (days_in_current_year + 1)
    baseload = [0.0] * 96 * (days_in_current_year + 1)
    contract_power = [17.0] * 96 * (days_in_current_year + 1)
    mock_vehicle_info = [
        VehicleTypeInfo(
            vehicle_type=VehicleType.VAN,
            nr_of_vehicles=1,
            power_usage=0.2,
            annual_km=2000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.BOXTRUCK,
            nr_of_vehicles=1,
            power_usage=0.5,
            annual_km=5000,
        ),
        VehicleTypeInfo(
            vehicle_type=VehicleType.SEMITRAILERTRUCK,
            nr_of_vehicles=1,
            power_usage=1.0,
            annual_km=10000,
        ),
    ]
    opt = EnergyPodOptimization(
        arrival_time="08:00",
        departure_time="18:00",
        vehicle_info=mock_vehicle_info,
        contract_connection_power=contract_power,
        max_connection_power=17,
        charge_point_power=200,
        battery_size=100,
        datetimes=datetimes,
        energy_prices=energy_prices,
        baseload=baseload,
    )

    # Act
    optimization_results = opt.calculate_optimization_results()
    discharge = [max(0, entry.battery_power) for entry in optimization_results.optimized_energy]
    charge = [min(0, entry.battery_power) for entry in optimization_results.optimized_energy]

    # Assert
    assert sum([entry.cp_power for entry in optimization_results.optimized_energy]) / 4 == opt.E_Vdem * 365
    assert pytest.approx(sum(charge) + sum(discharge), rel=1e-9) == 0
