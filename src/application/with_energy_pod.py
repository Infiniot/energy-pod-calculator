"""Contains functions to calculate the total power usage with EnergyPod."""

from __future__ import annotations

from datetime import datetime, timedelta
from functools import reduce

import numpy as np
from fastapi import HTTPException

from src.application.baseload_profile import (
    calculate_shifted_baseload_profiles,
)
from src.application.energy_prices import load_interpolated_energy_prices_year
from src.application.investment_costs import calculate_investment_costs_ep
from src.application.optimization import EnergyPodOptimization
from src.config import (
    days_in_current_year,
    ere_tariff,
    first_day_of_year,
)
from src.custom_exceptions.optimization_error import OptimizationError
from src.domain.energy_dto import EnergyDTO
from src.domain.energy_pod import BatteryResults, EnergyPod, EnergyPodResults


class EnergyPodPower:
    """Creates an instance to calculate the power needed by the EnergyPod."""

    def __init__(self, energy_pod_input: EnergyDTO) -> None:
        """Initializes the EnergyPodPower class."""
        self.energy_pod_input = energy_pod_input
        self._calculate_time_features()
        self._calculate_baseload()
        self._load_energy_prices()
        self._calculate_connection_power()
        self._load_vehicle_information()

    def _calculate_time_features(self) -> None:
        """Calculates and initializes time related features and variables."""
        # Determine current datetime
        self.start_datetime = first_day_of_year

        self.departure_time_delta = (
            reduce(lambda x, y: x * 4 + y // 15, map(int, self.energy_pod_input.departure_time.split(":")))
            if self.energy_pod_input.departure_time < self.energy_pod_input.arrival_time
            else 0
        )
        self.overnight_charging = self.departure_time_delta > 0

    def _calculate_baseload(self) -> None:
        """Calculates baseload and returns baseload in a dataframe."""
        self.baseload = calculate_shifted_baseload_profiles(
            self.energy_pod_input.baseload,
            overnight_charging=self.overnight_charging,
        )
        self.baseload_powers = [b.power for b in self.baseload]

    def _load_energy_prices(self) -> None:
        """Loads energy prices for a year."""
        self.energy_prices_year = load_interpolated_energy_prices_year(overnight_charging=self.overnight_charging)
        self.energy_prices = [e.price for e in self.energy_prices_year]

    def _calculate_connection_power(self) -> None:
        """Calculates the contract connection power and max connection power."""
        self.contract_connection_power_year = self.energy_pod_input.calculate_contracted_capacity_year(
            overnight_charging=self.overnight_charging
        )
        self.contract_connection_power = [c.power for c in self.contract_connection_power_year]
        self.max_connection_power = self.energy_pod_input.calculate_connection_capacity()

    def _load_vehicle_information(self) -> None:
        """Loads vehicle information for all vehicle types."""
        self.vehicle_info = self.energy_pod_input.vehicle_info.get_vehicle_infos()

    def _calculate_worst_days(self) -> tuple[datetime, datetime, datetime]:
        """Calculates the worst days for energy costs and the number and power of capacity exceedances."""
        worst_day_energy_costs_int = int(np.argmax(np.array(self.energy_costs_day)))
        worst_day_energy_costs = self.start_datetime + timedelta(days=worst_day_energy_costs_int)

        worst_day_nr_exceedances_int = int(np.argmax(np.array(self.nr_capacity_exceedances_day)))
        worst_day_nr_exceedances = self.start_datetime + timedelta(days=worst_day_nr_exceedances_int)

        worst_day_power_exceedances_int = int(np.argmax(np.array(self.power_capacity_exceedances_day)))
        worst_day_power_exceedances = self.start_datetime + timedelta(days=worst_day_power_exceedances_int)

        return worst_day_energy_costs, worst_day_nr_exceedances, worst_day_power_exceedances

    def _calculate_investment_costs(self) -> tuple[float, float]:
        """Calculates the investment costs for the battery and charge points."""
        total_vehicles = self.energy_pod_input.vehicle_info.get_total_nr_of_vehicles()
        return calculate_investment_costs_ep(
            self.battery_capacity_optimization,
            total_vehicles,
            self.energy_pod_input.charge_point_power,
        )

    def calculate_energy_pod_power_results(self) -> EnergyPodResults:
        """Calculates the power usage, the costs and the worst days for the scenario with EnergyPod."""
        datetimes = [self.start_datetime + timedelta(minutes=15 * t) for t in range(96 * (days_in_current_year + 1))]

        try:
            opt_prob_init = EnergyPodOptimization(
                arrival_time=self.energy_pod_input.arrival_time,
                departure_time=self.energy_pod_input.departure_time,
                vehicle_info=self.vehicle_info,
                contract_connection_power=self.contract_connection_power,
                max_connection_power=self.max_connection_power,
                charge_point_power=self.energy_pod_input.charge_point_power,
                battery_size=self.energy_pod_input.battery_capacity,
                datetimes=datetimes,
                energy_prices=self.energy_prices,
                baseload=self.baseload_powers,
            )
            optimization_results = opt_prob_init.calculate_optimization_results()
            self.optimization_energy_results = optimization_results.optimized_energy
            self.battery_capacity_optimization = optimization_results.battery_capacity

            self.yearly_energy_costs = optimization_results.total_energy_costs
            self.yearly_costs_capacity_exceedances = optimization_results.total_costs_capacity_exceedances

            self.energy_price_markup_costs = optimization_results.energy_price_markup_costs
            self.energy_tax_costs = optimization_results.energy_tax_costs

            self.energy_costs_day = optimization_results.total_energy_costs_day
            self.nr_capacity_exceedances_day = optimization_results.nr_capacity_exceedances_day
            self.power_capacity_exceedances_day = optimization_results.power_capacity_exceedances_day

        except OptimizationError as e:
            raise HTTPException(status_code=500, detail=e.message) from e

        worst_day_energy_costs, worst_day_nr_exceedances, worst_day_power_exceedances = self._calculate_worst_days()
        battery_cost, cp_cost = self._calculate_investment_costs()

        battery_results = BatteryResults(
            capacity=self.battery_capacity_optimization,
            power=int(self.battery_capacity_optimization / 2),
            cost=battery_cost,
        )

        ere_reduction_costs = sum([opt.cp_power * 0.25 for opt in self.optimization_energy_results]) * ere_tariff
        total_energy_costs_year = sum(self.energy_costs_day)

        return EnergyPodResults(
            consumption=[
                EnergyPod(
                    datetime=self.optimization_energy_results[i].datetime.strftime("%m/%d/%Y %H:%M"),
                    baseload_power=self.baseload_powers[i],
                    contract_power=round(self.contract_connection_power[i], 2),
                    charge_point_power=round(
                        self.optimization_energy_results[i].cp_power
                        + min(0, self.optimization_energy_results[i].battery_power),
                        2,
                    ),
                    battery_charge_power=round(max(0, self.optimization_energy_results[i].battery_power), 2),
                    battery_discharge_power=round(abs(min(0, self.optimization_energy_results[i].battery_power)), 2),
                )
                for i in range(len(self.optimization_energy_results))
            ],
            battery_results=battery_results,
            yearly_energy_costs=self.energy_costs_day,
            total_yearly_energy_costs=round(total_energy_costs_year, 2),
            energy_price_markup_costs=self.energy_price_markup_costs,
            energy_tax_costs=self.energy_tax_costs,
            ere_reduction_costs=round(ere_reduction_costs, 2),
            yearly_costs_capacity_exceedances=round(self.yearly_costs_capacity_exceedances, 2),
            investment_costs_cp=cp_cost,
            nr_capacity_exceedances_year=self.nr_capacity_exceedances_day,
            power_capacity_exceedances_year=self.power_capacity_exceedances_day,
            worst_day_energy_costs=worst_day_energy_costs,
            worst_day_nr_exceedances=worst_day_nr_exceedances,
            worst_day_power_exceedances=worst_day_power_exceedances,
        )
