"""Contains functions to calculate the investment costs."""

from __future__ import annotations

from src.config import battery_price_per_kwh, cp_price_per_kw


def calculate_investment_costs_battery(battery_size: int) -> float:
    """Calculates the investment costs for the total battery system.

    Args:
        battery_size: Size of the battery in kWh.
    """
    return float(round(battery_price_per_kwh * battery_size, 2))


def calculate_investment_costs_charge_point(nr_of_vehicles: int, charge_point_power: int) -> float:
    """Calculates the investment costs for the charge points.

    Args:
        nr_of_vehicles: The total number of vehicles. We assume that we have one charge point per vehicle.
        charge_point_power: The max power of a charge point.
    """
    return float(round(nr_of_vehicles * cp_price_per_kw * charge_point_power, 2))


def calculate_investment_costs_ep(
    battery_capacity: int, total_vehicles: int, charge_point_power: int
) -> tuple[float, float]:
    """Calculates the total investment costs for the scenario with EnergyPod."""
    battery_cost = calculate_investment_costs_battery(battery_capacity)
    cp_cost = calculate_investment_costs_charge_point(total_vehicles, charge_point_power)
    return battery_cost, cp_cost
