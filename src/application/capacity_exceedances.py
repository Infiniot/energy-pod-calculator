"""Contains functions to calculate the grid connection capacity exceedances."""

import numpy as np

from src.application.energy_prices import load_interpolated_energy_prices_year
from src.config import days_in_current_year
from src.domain.capacity_exceedances import CapacityExceedancesNoEP
from src.domain.without_energy_pod import EnergyWithoutEP


def calculate_capacity_exceedances(
    energy_consumption_year: list[EnergyWithoutEP],
) -> tuple[list[int], list[float]]:
    """Calculates the number of times the connection capacity is exceeded in a year.

    Args:
        energy_consumption_year: The energy consumption without EnergyPod over a year.
    """
    nr_exceedances = []
    power_exceedances = []

    ec_day = np.split(np.array(energy_consumption_year), days_in_current_year)

    for day in range(days_in_current_year):
        exceedances = []
        for quarter in range(len(ec_day[day])):
            exceeded = round(
                ec_day[day][quarter].contract_power
                - ec_day[day][quarter].baseload_power
                - ec_day[day][quarter].charge_point_power,
                4,
            )
            if exceeded < 0:
                exceedances.append(-exceeded)
        nr_exceedances.append(len(exceedances))
        power_exceedances.append(np.round(np.sum(exceedances) / 4, 2))

    return nr_exceedances, power_exceedances


def calculate_capacity_exceedances_year_no_ep(
    energy_consumption_year: list[EnergyWithoutEP],
) -> CapacityExceedancesNoEP:
    """Calculates the number of times the connection capacity is exceeded in a year without EnergyPod.

    Args:
        energy_consumption_year: The energy consumption without EnergyPod over a year.
    """
    # Load energy prices for a year
    energy_prices_year = load_interpolated_energy_prices_year()
    max_energy_price_hour = np.max(np.max([e.price for e in energy_prices_year])) * 4

    nr_exceedances, power_exceedances = calculate_capacity_exceedances(energy_consumption_year)
    yearly_costs_capacity_exceedances = float(round(sum(power_exceedances) * max_energy_price_hour * 3, 2))

    return CapacityExceedancesNoEP(
        nr_capacity_exceedances_year=nr_exceedances,
        power_capacity_exceedances_year=power_exceedances,
        yearly_costs_capacity_exceedances=yearly_costs_capacity_exceedances,
    )
