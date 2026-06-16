"""Unit tests for application.investment_costs using Arrange/Act/Assert (AAA).

Tests cover:
- calculate_investment_costs_battery calculating battery costs
- calculate_investment_costs_charge_point calculating charge point costs
- calculate_investment_costs_ep calculating total EnergyPod investment costs

Each test follows the AAA pattern and returns None.
"""

from src.application.investment_costs import (
    calculate_investment_costs_battery,
    calculate_investment_costs_charge_point,
    calculate_investment_costs_ep,
)
from src.config import battery_price_per_kwh, cp_price_per_kw


def test_calculate_investment_costs_battery_calculates_costs() -> None:
    """Arrange: Prepare a battery size in kWh.

    Act: Call calculate_investment_costs_battery.
    Assert: Returned battery cost is correct.
    """
    # Arrange
    battery_size = 100

    # Act
    result = calculate_investment_costs_battery(battery_size)

    expected_cost = battery_size * battery_price_per_kwh

    # Assert
    assert isinstance(result, float)
    assert result == expected_cost


def test_calculate_investment_costs_charge_point_calculates_costs() -> None:
    """Arrange: Prepare a number of vehicles.

    Act: Call calculate_investment_costs_charge_point.
    Assert: Returned charge point cost is correct.
    """
    # Arrange
    nr_of_vehicles = 5
    charge_point_power = 200

    # Act
    result = calculate_investment_costs_charge_point(nr_of_vehicles, charge_point_power)

    expected_cost = nr_of_vehicles * 200 * cp_price_per_kw

    # Assert
    assert isinstance(result, float)
    assert result == expected_cost


def test_calculate_investment_costs_ep_calculates_total_costs() -> None:
    """Arrange: Prepare a battery size and number of vehicles.

    Act: Call calculate_investment_costs_ep.
    Assert: Returned battery and charge point costs are correct.
    """
    # Arrange
    battery_capacity = 100
    total_vehicles = 5
    charge_point_power = 200

    # Act
    battery_cost, cp_cost = calculate_investment_costs_ep(battery_capacity, total_vehicles, charge_point_power)

    expected_battery_cost = battery_capacity * battery_price_per_kwh
    expected_cp_cost = total_vehicles * charge_point_power * cp_price_per_kw

    # Assert
    assert isinstance(battery_cost, float)
    assert isinstance(cp_cost, float)
    assert battery_cost == expected_battery_cost
    assert cp_cost == expected_cp_cost
