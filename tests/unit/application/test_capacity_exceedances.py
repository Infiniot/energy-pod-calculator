"""Unit tests for application.capacity_exceedances using Arrange/Act/Assert (AAA).

Tests cover:
- calculate_capacity_exceedances_year_no_ep counting exceedances
- calculate_capacity_exceedances_year_ep counting exceedances

Each test follows Arrange / Act / Assert and returns None.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.application.capacity_exceedances import (
    calculate_capacity_exceedances,
    calculate_capacity_exceedances_year_no_ep,
)
from src.application.small_consumer_connection import calculate_small_consumer_connection
from src.config import days_in_current_year, first_day_of_year
from src.domain.baseload_profile import BaseloadProfile
from src.domain.capacity_exceedances import CapacityExceedancesNoEP
from src.domain.energy_dto import EnergyDTOSmallConsumer
from src.domain.vehicle_info import VehicleInfoDTO, VehicleTypeInfoDTO
from src.domain.without_energy_pod import EnergyWithoutEP


def test_calculate_capacity_exceedances_counts_exceedances() -> None:
    """Arrange: Prepare a list with the energy consumption for the current year.

    Act: Call calculate_capacity_exceedances.
    Assert: Returned number of exceedances and exceeded power are correct.
    """
    # Arrange
    mock_datetimes = [
        (first_day_of_year + timedelta(minutes=15 * t)).isoformat() for t in range(days_in_current_year * 96)
    ]

    mock_energy_consumption = [
        EnergyWithoutEP(datetime=mock_datetimes[t], baseload_power=2, contract_power=5, charge_point_power=1)
        for t in range(len(mock_datetimes) - 5 * 96)
    ] + [
        EnergyWithoutEP(datetime=mock_datetimes[t], baseload_power=2, contract_power=5, charge_point_power=20)
        for t in range(len(mock_datetimes) - 5 * 96, len(mock_datetimes))
    ]

    # Act
    result = calculate_capacity_exceedances(mock_energy_consumption)

    expected_nr_exceedances = [0] * (days_in_current_year - 5) + [96] * 5
    expected_power_exceedances = [0] * (days_in_current_year - 5) + [17 * 96 / 4] * 5

    # Assert
    assert isinstance(result[0], list)
    assert len(result[0]) == len(expected_nr_exceedances)
    assert isinstance(result[1], list)
    assert len(result[1]) == len(expected_power_exceedances)

    for day in range(len(result[0])):
        assert isinstance(result[0][day], int)
        assert result[0][day] == expected_nr_exceedances[day]

    for day in range(len(result[1])):
        assert isinstance(result[1][day], float)
        assert result[1][day] == expected_power_exceedances[day]


def test_calculate_capacity_exceedances_year_no_ep_counts_exceedances() -> None:
    """Arrange: Build a list of consumption entries with known sums.

    Act: Call calculate_capacity_exceedances_year_no_ep.
    Assert: Returned count equals expected number of exceedances.
    """
    # Arrange
    mock_without_ep_input = EnergyDTOSmallConsumer(
        vehicle_info=VehicleInfoDTO(
            vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.2, annual_km=2000),
            boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.5, annual_km=5000),
            semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1.0, annual_km=7000),
        ),
        arrival_time="08:00",
        departure_time="18:00",
        baseload=[BaseloadProfile(datetime=datetime(2025, 1, 1, tzinfo=ZoneInfo("Europe/Amsterdam")), power=0.0)]
        * 96
        * 365,
        connection_category="3 x 25A",
        zip_code="1111AA",
        battery_capacity=None,
        charge_point_power=200,
    )
    capacity = calculate_small_consumer_connection(
        mock_without_ep_input.connection_category
    )  # compute capacity used by function

    now = first_day_of_year
    days = days_in_current_year

    # items: one below, one equal, one above
    below = EnergyWithoutEP(
        datetime=now.strftime("%m/%d/%Y %H:%M"),
        baseload_power=5,
        contract_power=capacity,
        charge_point_power=5,
    )  # 10 <= capacity
    equal = EnergyWithoutEP(
        datetime=(now + timedelta(minutes=15)).strftime("%m/%d/%Y %H:%M"),
        baseload_power=capacity - 5,
        contract_power=capacity,
        charge_point_power=5,
    )  # equals capacity
    above = EnergyWithoutEP(
        datetime=(now + timedelta(minutes=30)).strftime("%m/%d/%Y %H:%M"),
        baseload_power=capacity,
        contract_power=capacity,
        charge_point_power=1,
    )  # > capacity
    data = [below, equal, above] + [
        EnergyWithoutEP(
            datetime=(now + timedelta(minutes=45 + 15 * i)).strftime("%m/%d/%Y %H:%M"),
            baseload_power=capacity - 5,
            contract_power=capacity,
            charge_point_power=5,
        )
        for i in range(96 * days - 3)
    ]
    expected_nr_exceedances_year = [1] + [0] * (days - 1)
    expected_power_exceedances_year = [0.25] + [0] * (days - 1)
    expected_yearly_costs_capacity_exceedances = 2.62

    # Act
    result = calculate_capacity_exceedances_year_no_ep(data)

    # Assert
    assert isinstance(result, CapacityExceedancesNoEP)
    assert hasattr(result, "nr_capacity_exceedances_year")
    assert len(result.nr_capacity_exceedances_year) == len(expected_nr_exceedances_year)
    assert result.nr_capacity_exceedances_year == expected_nr_exceedances_year
    assert hasattr(result, "power_capacity_exceedances_year")
    assert len(result.power_capacity_exceedances_year) == len(expected_power_exceedances_year)
    assert result.power_capacity_exceedances_year == expected_power_exceedances_year
    assert hasattr(result, "yearly_costs_capacity_exceedances")
    assert result.yearly_costs_capacity_exceedances == expected_yearly_costs_capacity_exceedances
