"""Contains function to calculate the energy costs and highest energy costs savings."""

from __future__ import annotations

from datetime import timedelta

import numpy as np

from src.application.energy_prices import load_interpolated_energy_prices_year
from src.config import (
    days_in_current_year,
    energy_price_markup,
    ere_tariff,
    first_day_of_year,
)
from src.domain.energy_costs import EnergyCostsYearWithoutEP, HighestEnergyCostsSavings
from src.domain.without_energy_pod import EnergyWithoutEP


def calculate_energy_costs_year_without_ep(
    energy_consumption_year: list[EnergyWithoutEP],
    *,
    overnight_charging: bool = False,
) -> EnergyCostsYearWithoutEP:
    """Calculates the energy costs of power consumption without EnergyPod over a year.

    Args:
        energy_consumption_year: list of EnergyWithoutEP entries over a year.
        overnight_charging: Boolean that indicates if vehicles can charge overnight.
    """
    start_datetime = first_day_of_year
    days = days_in_current_year

    # Load energy prices for a year
    energy_prices_year = load_interpolated_energy_prices_year(overnight_charging=overnight_charging)

    cps_total_year = np.array([cp.charge_point_power for cp in energy_consumption_year]) * 0.25
    energy_costs = cps_total_year * np.array([e.price for e in energy_prices_year])[: len(cps_total_year)]

    energy_price_markup_costs = np.round(np.sum(cps_total_year * energy_price_markup), 2)
    energy_tax_costs = calculate_energy_tax(np.sum(cps_total_year))

    ere_reduction_costs = round(np.sum(cps_total_year) * ere_tariff, 2)

    energy_costs_day = np.round(np.sum(np.split(energy_costs, days), axis=1), 2)
    worst_day_energy_costs = start_datetime + timedelta(days=int(np.argmax(energy_costs_day)))

    return EnergyCostsYearWithoutEP(
        energy_costs_day=energy_costs_day,
        worst_day_energy_costs=worst_day_energy_costs,
        ere_reduction_costs=ere_reduction_costs,
        energy_price_markup_costs=energy_price_markup_costs,
        energy_tax_costs=energy_tax_costs,
    )


def calculate_highest_energy_costs_savings(
    energy_costs_no_ep: list[float], energy_costs_ep: list[float]
) -> HighestEnergyCostsSavings:
    """Calculates the day with the highest absolute energy costs savings.

    Args:
        energy_costs_no_ep: List of total energy costs for each day of the year in the scenario without EnergyPod.
        energy_costs_ep: List of total energy costs for each day of the year in the scenario with EnergyPod.
    """
    energy_costs_diff = np.abs(np.array(energy_costs_no_ep) - np.array(energy_costs_ep))
    day_highest_savings_index = np.argmax(energy_costs_diff)
    day_highest_savings = first_day_of_year + timedelta(days=int(day_highest_savings_index))

    return HighestEnergyCostsSavings(
        datetime=day_highest_savings,
        absolute_savings=float(round(energy_costs_diff[day_highest_savings_index])),
        energy_costs_no_ep=energy_costs_no_ep[day_highest_savings_index],
        energy_costs_ep=energy_costs_ep[day_highest_savings_index],
    )


def calculate_energy_tax(yearly_energy_consumption: float) -> float:
    """Calculates the energy costs for energy tax based on the total yearly energy consumption.

    Args:
        yearly_energy_consumption: Total yearly energy consumption used for the charging of vehicles.
    """
    energy_tax_scale: dict[str, list] = {
        "scale": [1, 2, 3, 4, 5],
        "lower": [0, 2900, 10000, 50000, 10000000],
        "upper": [2900, 10000, 50000, 10000000, float("inf")],
        "price": [0.10154, 0.10154, 0.06937, 0.03868, 0.00321],
    }

    price = 0
    for scale in range(len(energy_tax_scale["scale"])):
        if yearly_energy_consumption >= energy_tax_scale["lower"][scale]:
            price += (
                min(energy_tax_scale["upper"][scale], yearly_energy_consumption) - energy_tax_scale["lower"][scale]
            ) * energy_tax_scale["price"][scale]

    return round(price, 2)
