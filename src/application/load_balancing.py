"""Contains functions to calculate if the current capacity is sufficient based on load balancing."""

from enum import Enum
from functools import reduce

import numpy as np

from src.application.baseload_profile import (
    calculate_shifted_baseload_profiles,
)
from src.config import battery_step_size, days_in_current_year, max_battery_steps
from src.domain.energy_dto import EnergyDTO
from src.utils.time_frame import calculate_indices_arrival_departure_time


class ConnectionUpdateType(Enum):
    """Enum types for the type of connection update."""

    INCREASE = 1
    CONSTANT = 0
    DECREASE = -1


class LoadBalancingOrchestrator:
    """Calculate the energy consumption using load balancing."""

    def __init__(self, energy_dto: EnergyDTO) -> None:
        """Initializes the LoadBalancing class."""
        self.energy_dto = energy_dto

        # Determine the current datetime
        self.days = days_in_current_year

        self._calculate_baseload()
        self._calculate_connection_power()
        self._calculate_charging_power()
        self._initialize_battery_charging()

    def _calculate_baseload(self) -> None:
        """Calculates baseload and returns baseload as a list."""
        baseload = calculate_shifted_baseload_profiles(self.energy_dto.baseload)
        self.baseload_profiles = np.array([x.power for x in baseload])

    def _calculate_connection_power(self) -> None:
        """Calculates the connection power and returns the connection power as a list."""
        connection_power = self.energy_dto.calculate_contracted_capacity_year()
        self.connection_power = np.array([x.power for x in connection_power])

    def _calculate_charging_power(self) -> None:
        """Determines the charging power for a whole year based on load balancing."""
        total_energy_demand_day = self.energy_dto.vehicle_info.get_total_energy_demand_vehicle_types()

        self.t_arr = self.energy_dto.arrival_time
        self.t_dep = self.energy_dto.departure_time

        self.t_arr_ind, self.t_dep_ind = calculate_indices_arrival_departure_time(
            self.energy_dto.arrival_time, self.energy_dto.departure_time
        )

        charging_time_quarter = self.t_dep_ind - self.t_arr_ind

        power_per_quarter = (total_energy_demand_day * 4) / charging_time_quarter

        self.charging_power = np.zeros(96 * self.days)
        self.charging_indices = [
            list(range(self.t_arr_ind + day * 96, min(self.t_dep_ind + day * 96, self.days * 96)))
            for day in range(self.days)
        ]
        if self.t_dep < self.t_arr:
            self.charging_indices = [list(range(self.t_dep_ind - 96)), *self.charging_indices]

        self.charging_indices_day = reduce(lambda x, y: x + y, self.charging_indices)

        self.charging_power[self.charging_indices_day] = power_per_quarter

    def _initialize_battery_charging(self) -> None:
        """Returns a list of zeros to represent the battery charging."""
        self.battery_charging = np.zeros(96 * self.days)

    def calculate_battery_charging(self) -> None:
        """Distributes battery charging over the appropriate time periods, considering load and vehicle charging."""
        if self.energy_dto.battery_capacity is None:
            battery_for_load_balancer = (
                min(
                    (self.energy_dto.vehicle_info.get_total_energy_demand_vehicle_types() // battery_step_size) + 1,
                    max_battery_steps,
                )
            ) * battery_step_size
        else:
            battery_for_load_balancer = self.energy_dto.battery_capacity

        # Calculate the reduction in vehicle charging demand as a result of having the battery.
        # Reduction cannot be greater than the predicted charging volume
        charging_power_reduction = np.minimum(
            battery_for_load_balancer * 4 / (self.t_dep_ind - self.t_arr_ind),
            self.charging_power[self.charging_indices_day],
        )

        # Charging power is reduced to simulate the pressence of a battery
        self.charging_power[self.charging_indices_day] -= charging_power_reduction

        # The charging of the battery is simulated to be evenly distributed across each day.
        self.battery_charging += (
            min(
                battery_for_load_balancer,
                self.energy_dto.vehicle_info.get_total_energy_demand_vehicle_types(),
            )
            / 24
        )

        # distribute charging to battery to periods of lower baseload
        self.battery_charging += np.average(self.baseload_profiles)
        self.battery_charging -= self.baseload_profiles

        negative_charging = -np.sum(self.battery_charging[self.battery_charging < 0])
        self.battery_charging[self.battery_charging > 0] -= negative_charging / len(
            self.battery_charging[self.battery_charging > 0]
        )
        self.battery_charging[self.battery_charging < 0] = 0

    def _calculate_power_abundances_shortages(self) -> None:
        """Determines if the current capacity is sufficient based on the provided input."""
        self.available_power = (
            self.connection_power - self.baseload_profiles - self.charging_power - self.battery_charging
        )

        nr_power_shortages = np.sum(self.available_power[self.charging_indices_day] < 0)
        nr_power_abundances = np.sum(self.available_power[self.charging_indices_day] > 0)

        self.percentage_power_shortages = (nr_power_shortages / len(self.charging_indices_day)) * 100
        self.percentage_power_abundances = (nr_power_abundances / len(self.charging_indices_day)) * 100

    def _calculate_connection_update_decision(self) -> ConnectionUpdateType:
        """Returns the type of connection update based on load balancing."""
        self._threshold = 10
        self._calculate_power_abundances_shortages()

        if self.percentage_power_shortages > self._threshold:
            return ConnectionUpdateType.INCREASE
        if (self.percentage_power_shortages <= self._threshold) and (
            self.percentage_power_abundances > self._threshold
        ):
            return ConnectionUpdateType.DECREASE
        return ConnectionUpdateType.CONSTANT

    def calculate_size_connection_update(self) -> float:
        """Calculates the size of the connection update."""
        connection_update_type = self._calculate_connection_update_decision()
        match connection_update_type:
            case ConnectionUpdateType.INCREASE:
                connection_update = np.min(self.available_power[self.available_power < 0])
            case ConnectionUpdateType.DECREASE:
                connection_update = np.min(self.available_power[self.available_power > 0])
            case _:
                connection_update = 0
        return -round(connection_update, 2)
