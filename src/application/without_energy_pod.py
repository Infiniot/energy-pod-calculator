"""Contains functions to calculate the total power usage without EnergyPod."""

from __future__ import annotations

import numpy as np

from src.application.baseload_profile import (
    calculate_shifted_baseload_profiles,
)
from src.application.capacity_exceedances import calculate_capacity_exceedances_year_no_ep
from src.application.charging_profiles_without_ep import ChargingProfilesWithoutEP
from src.application.costs_uncharged_power import calculate_costs_uncharged_power
from src.application.energy_costs import calculate_energy_costs_year_without_ep
from src.application.investment_costs import calculate_investment_costs_charge_point
from src.custom_exceptions.charging_window_error import ChargingWindowError
from src.domain.charging_profiles import ChargingProfileDTO
from src.domain.energy_dto import EnergyDTO
from src.domain.without_energy_pod import EnergyResultsWithoutEP, EnergyWithoutEP, ResultWithoutEP
from src.logger import logger


def calculate_power_without_energy_pod(
    energy_usage_dto: EnergyDTO, *, overnight_charging: bool = False
) -> EnergyResultsWithoutEP:
    """Calculates the energy used based on the input.

    The energy usage is a combination of the energy used for charging and the baseload profile for every 15 minutes.

    Args:
        energy_usage_dto: Data transfer object containing input parameters for energy usage.
        overnight_charging: Boolean that indicates if vehicles can charge overnight.
    """
    connection_power = energy_usage_dto.calculate_contracted_capacity_year(overnight_charging=overnight_charging)
    charging_profiles_input = ChargingProfileDTO(
        arrival_time=energy_usage_dto.arrival_time,
        departure_time=energy_usage_dto.departure_time,
        connection_power=connection_power,
    )

    vehicle_info = energy_usage_dto.vehicle_info.get_vehicle_infos()

    baseload_profiles = calculate_shifted_baseload_profiles(
        energy_usage_dto.baseload,
        overnight_charging=overnight_charging,
    )
    charge_point_power = energy_usage_dto.charge_point_power

    try:
        charging_profiles_without_ep_init = ChargingProfilesWithoutEP(
            charging_profiles_input, vehicle_info, baseload_profiles, charge_point_power
        )
        charging_profiles_without_ep = charging_profiles_without_ep_init.calculate_charging_profiles_without_ep()
    except ChargingWindowError as e:
        logger.error(e)

    return EnergyResultsWithoutEP(
        energy_consumption=[
            EnergyWithoutEP(
                datetime=charging_profiles_without_ep.charging_profiles[i].datetime.strftime("%m/%d/%Y %H:%M"),
                baseload_power=baseload_profiles[i].power,
                contract_power=round(connection_power[i].power, 2),
                charge_point_power=round(charging_profiles_without_ep.charging_profiles[i].power, 2),
            )
            for i in range(len(charging_profiles_without_ep.charging_profiles))
        ],
        uncharged_power=charging_profiles_without_ep.uncharged_power,
        vehicles_not_fully_charged=charging_profiles_without_ep.vehicles_not_fully_charged,
        worst_day_uncharged_power=charging_profiles_without_ep.worst_day_uncharged_power,
        worst_day_vehicles=charging_profiles_without_ep.worst_day_vehicles,
    )


def calculate_results_without_energypod(without_energy_pod_input: EnergyDTO) -> ResultWithoutEP:
    """Calculate the results for the without EnergyPod scenario."""
    if (
        (without_energy_pod_input.arrival_time != "")
        and (without_energy_pod_input.departure_time != "")
        and (without_energy_pod_input.departure_time < without_energy_pod_input.arrival_time)
    ):
        overnight_charging = True
    else:
        overnight_charging = False

    results_without_ep = calculate_power_without_energy_pod(
        without_energy_pod_input, overnight_charging=overnight_charging
    )
    energy_costs = calculate_energy_costs_year_without_ep(
        energy_consumption_year=results_without_ep.energy_consumption,
        overnight_charging=overnight_charging,
    )
    capacity_exceedances_year = calculate_capacity_exceedances_year_no_ep(results_without_ep.energy_consumption)
    yearly_costs_uncharged_power = calculate_costs_uncharged_power(results_without_ep.uncharged_power)

    total_nr_of_vehicles = (
        without_energy_pod_input.vehicle_info.vans.nr_of_vehicles
        + without_energy_pod_input.vehicle_info.boxtrucks.nr_of_vehicles
        + without_energy_pod_input.vehicle_info.semitrailertrucks.nr_of_vehicles
    )
    investment_costs_cps = calculate_investment_costs_charge_point(
        nr_of_vehicles=total_nr_of_vehicles,
        charge_point_power=without_energy_pod_input.charge_point_power,
    )

    total_energy_costs_year = np.sum(energy_costs.energy_costs_day)

    return ResultWithoutEP(
        consumption=results_without_ep.energy_consumption,
        total_yearly_energy_costs=round(total_energy_costs_year, 2),
        yearly_costs=energy_costs.energy_costs_day,
        energy_price_markup_costs=energy_costs.energy_price_markup_costs,
        energy_tax_costs=energy_costs.energy_tax_costs,
        ere_reduction_costs=energy_costs.ere_reduction_costs,
        nr_capacity_exceedances_year=capacity_exceedances_year.nr_capacity_exceedances_year,
        power_capacity_exceedances_year=capacity_exceedances_year.power_capacity_exceedances_year,
        yearly_costs_capacity_exceedances=capacity_exceedances_year.yearly_costs_capacity_exceedances,
        uncharged_power=results_without_ep.uncharged_power,
        yearly_costs_uncharged_power=yearly_costs_uncharged_power,
        vehicles_not_fully_charged=results_without_ep.vehicles_not_fully_charged,
        investment_costs=investment_costs_cps,
        worst_day_uncharged_power=results_without_ep.worst_day_uncharged_power,
        worst_day_vehicles=results_without_ep.worst_day_vehicles,
        worst_day_energy_costs=energy_costs.worst_day_energy_costs,
    )
