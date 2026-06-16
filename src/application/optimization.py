"""Contains functionality for optimizing charging sessions and battery usage."""

import time
from datetime import datetime

import numpy as np
from pulp import HiGHS, LpMinimize, LpProblem, LpVariable, lpSum, value

from src.application.energy_costs import calculate_energy_tax
from src.config import (
    battery_loss_charge,
    battery_loss_discharge,
    battery_price_per_kwh,
    battery_step_size,
    days_in_current_year,
    energy_price_markup,
    max_battery_steps,
    min_battery_steps,
)
from src.custom_exceptions.optimization_error import OptimizationError
from src.domain.energy_costs import EnergyCostsYearWithEP
from src.domain.optimized_energy import OptimizationResults, OptimizedEnergy
from src.domain.vehicle_info import VehicleType, VehicleTypeInfo


class EnergyPodOptimization:
    """Creates an instance of an optimization problem for charging sessions and battery usage in the EnergyPod."""

    def __init__(
        self,
        arrival_time: str,
        departure_time: str,
        vehicle_info: list[VehicleTypeInfo],
        contract_connection_power: list[float],
        max_connection_power: float,
        charge_point_power: int,
        battery_size: int | None,
        datetimes: list[datetime],
        energy_prices: list[float],
        baseload: list[float],
    ) -> None:
        """Initializes the EnergyPodOptimization class."""
        # Initialize energy pod input
        self.vehicle_info = vehicle_info
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.contract_connection_power = contract_connection_power
        self.max_connection_power = max_connection_power
        self.charge_point_power = charge_point_power
        self.battery_size = battery_size

        # Initialize energy prices and baseload
        self.datetimes = datetimes
        self.c_t = energy_prices
        self.baseload = baseload

        # Create input parameters
        self._create_input_parameters()

        # Initialize the optimization problem and its parameters
        self._initialize_optimization_parameters()

        # Add constraints related to the grid connection capacity
        self._add_grid_constraints()

        # Add constraints related to the vehicle and charge point power
        self._add_vehicle_power_constraints()

        # Add constraints related to the battery charge and discharge
        self._add_battery_constraints()

        # Add constraints related to the total power consumption
        self._add_energy_pod_constraints()

        # Add constraints related to the different costs
        self._add_cost_constraints()

        # Add objective function for the minimization problem
        self._add_minimization_problem()

    def _map_arrival_times(
        self, t_arr: str, days: int, stoch_times_arr: np.ndarray, nr_of_vehicles_present: np.ndarray
    ) -> tuple[dict[VehicleType, list[int]], np.ndarray]:
        """Maps the arrival times to indices over the time interval."""
        t_arr_split = time.strptime(t_arr, "%H:%M")
        t_arr_hours, t_arr_minutes = t_arr_split.tm_hour, t_arr_split.tm_min
        t_arr_per_type = {}
        self.first_arrival = int(t_arr_hours * 4 + t_arr_minutes // 15)

        vehicle_count = 0
        for vehicle_type_info in self.vehicle_info:
            nr_of_vehicles_type = vehicle_type_info.nr_of_vehicles
            arrival_times_type = []
            for t in range(days):
                for _ in range(int(nr_of_vehicles_type)):
                    arrival_minutes_stoch = t_arr_minutes + stoch_times_arr[vehicle_count]
                    arrival_time_int = t_arr_hours * 4 + int(arrival_minutes_stoch // 15)
                    arrival_times_type.append(arrival_time_int + t * 96)
                    vehicle_count += 1
                    nr_of_vehicles_present[arrival_time_int + t * 96 :] += 1
            t_arr_per_type[vehicle_type_info.vehicle_type] = arrival_times_type

        return t_arr_per_type, nr_of_vehicles_present

    def _map_departure_times(
        self, t_dep: str, t_arr: str, days: int, stoch_times_dep: np.ndarray, nr_of_vehicles_present: np.ndarray
    ) -> tuple[dict[VehicleType, list[int]], np.ndarray]:
        """Maps the departure times to indices over the time interval."""
        t_dep_split = time.strptime(t_dep, "%H:%M")
        t_dep_hours, t_dep_minutes = t_dep_split.tm_hour, t_dep_split.tm_min
        t_dep_per_type = {}
        self.t_ch_next_day = int(t_dep_hours * 4 + t_dep_minutes // 15)

        vehicle_count = 0
        for vehicle_type_info in self.vehicle_info:
            nr_of_vehicles_type = vehicle_type_info.nr_of_vehicles
            departure_times_type = []
            for t in range(days):
                for _ in range(int(nr_of_vehicles_type)):
                    departure_minutes_stoch = t_dep_minutes + stoch_times_dep[vehicle_count]
                    departure_time_int = t_dep_hours * 4 + int(departure_minutes_stoch // 15)
                    max_int = days * 96 + (t_dep < t_arr) * self.t_ch_next_day - 1
                    dep_time_in_year = departure_time_int + t * 96 + (t_dep < t_arr) * 96
                    if dep_time_in_year > max_int:
                        departure_times_type.append(max_int)
                    else:
                        departure_times_type.append(dep_time_in_year)
                        nr_of_vehicles_present[dep_time_in_year:] -= 1
                    vehicle_count += 1
            t_dep_per_type[vehicle_type_info.vehicle_type] = departure_times_type

        return t_dep_per_type, nr_of_vehicles_present

    def _map_times(
        self, days: int
    ) -> tuple[dict[VehicleType, list[int]], dict[VehicleType, list[int]], bool, np.ndarray]:
        """Maps the arrival and departure times to indices over the time interval.

        Args:
            t_0: Start datetime of the optimization.
            days: Number of days used in the optimization.
        """
        t_arr = self.arrival_time
        t_dep = self.departure_time

        overnight = t_dep < t_arr
        total_nr_of_vehicles = np.sum([days * vehicle_type.nr_of_vehicles for vehicle_type in self.vehicle_info])
        nr_of_vehicles_present = np.zeros(96 * (days_in_current_year + overnight), int)
        np_generator = np.random.default_rng()

        stoch_times_arr = np.astype(np_generator.normal(loc=0, scale=30, size=total_nr_of_vehicles), int)
        stoch_times_dep = np.astype(np_generator.normal(loc=0, scale=30, size=total_nr_of_vehicles), int)

        t_arr_total, nr_of_vehicles_present = self._map_arrival_times(
            t_arr, days, stoch_times_arr, nr_of_vehicles_present
        )
        t_dep_total, nr_of_vehicles_present = self._map_departure_times(
            t_dep, t_arr, days, stoch_times_dep, nr_of_vehicles_present
        )

        if overnight:
            self.time_day_offset = max(stoch_times_dep) // 15 + self.t_ch_next_day
        else:
            self.time_day_offset = 0

        return t_arr_total, t_dep_total, overnight, nr_of_vehicles_present

    def _convert_input(self, nr_days_year: int) -> dict:
        """Converts the frontend input to input for the optimization problem."""
        p_cp_max = self.charge_point_power

        per_day_demand = 0
        for v in self.vehicle_info:
            per_day_demand += int(v.calculate_energy_demand() * v.nr_of_vehicles)

        [t_arr, t_dep, overnight, nr_of_vehicles_present] = self._map_times(days=nr_days_year)

        p_min = 0
        p_max = p_cp_max

        return {
            "vehicle_demands": per_day_demand,
            "t_arr": t_arr,
            "t_dep": t_dep,
            "nr_of_vehicles_present": nr_of_vehicles_present,
            "P_min": p_min,
            "P_max": p_max,
            "overnight": overnight,
        }

    def _create_input_parameters(self) -> None:
        """Initializes the parameters used for optimization of the EnergyPod."""
        converted_input = self._convert_input(days_in_current_year)

        # Parameters related to vehicle information
        self.overnight = converted_input["overnight"]
        self.E_Vdem = converted_input["vehicle_demands"]  # The energy demand for each charging session in kWh
        self.t_arr = converted_input["t_arr"]  # The arrival time of each charging session
        self.t_dep = converted_input["t_dep"]  # The departure time of each charging session
        self.nr_of_vehicles_present = converted_input[
            "nr_of_vehicles_present"
        ]  # The number of vehicles at the charging pod at time t

        # Parameters related to grid
        self.pen = np.max(self.c_t) * 3  # The penalty for exceeding the grid capacity

        # Parameters related to charging sessions
        self.P_min = converted_input["P_min"]  # The minimum power in each charging session
        self.P_max = converted_input["P_max"]  # The maximum power in each charging session

        self.T = (
            range(96 * days_in_current_year + self.time_day_offset)
            if self.overnight
            else range(96 * days_in_current_year)
        )
        self.t_range = range(self.T.stop - 1)

    def _initialize_optimization_parameters(self) -> None:
        """Initializes the optimization problem and its paramaters."""
        # Linear optimization problem for minimizing the total costs
        self.prob = LpProblem("test", LpMinimize)

        # Cost variables
        self.C_EP = LpVariable("C_EP", lowBound=0)  # Total costs for power from grid used for charging sessions

        if self.max_connection_power != min(self.contract_connection_power):
            self.C_pen = LpVariable(
                "C_pen", lowBound=0
            )  # Penalty costs for exceding the current grid connection capacity

        # Power variables
        self.P_CP = LpVariable.dicts("P_CP", self.T, lowBound=0)  # Power used for each charging session per t
        self.P_B_pos = LpVariable.dicts(
            "P_b_pos", self.T, lowBound=0, cat="Continuous"
        )  # Power used from battery per t (Grid -> Battery)
        self.P_B_neg = LpVariable.dicts(
            "P_B_neg", self.T, lowBound=0, cat="Continuous"
        )  # Power used from battery per t (Battery -> Vehicle)
        self.P_EP = LpVariable.dicts("P_EP", self.T, lowBound=0)  # Total power used per t
        if self.max_connection_power != min(self.contract_connection_power):
            self.P_pen = LpVariable.dicts(
                "P_pen", self.T, lowBound=0
            )  # Total power that exceeds the current grid connection capacity

        # Battery state of charge variable
        self.SoC = LpVariable.dicts("SoC", range(self.T.stop + 1), lowBound=0)
        self.P_b_pos = LpVariable.dicts("P_b_pos", self.T, lowBound=0, cat="Continuous")  # charging activation

        # Battery maximum capacity variable
        self.Q: LpVariable
        if self.battery_size is None:
            self.Q = LpVariable("Q", lowBound=min_battery_steps, upBound=max_battery_steps, cat="Integer")
        else:
            self.Q = LpVariable("Q", cat="Continuous")

        # Binary variables
        self.phi = LpVariable.dicts("phi", self.T, cat="Binary")  # charging activation

    def _add_grid_constraints(self) -> None:
        """Adds constraints related to the grid connection capacity.

        A constraint is added to ensure that the total EnergyPod power stays below the connection capacity.
        """
        if self.max_connection_power != min(self.contract_connection_power):
            for t in self.T:
                self.prob += self.P_pen[t] <= self.max_connection_power - self.contract_connection_power[t]
                self.prob += self.P_EP[t] + self.baseload[t] - self.P_pen[t] <= self.contract_connection_power[t]
        else:
            for t in self.T:
                self.prob += self.P_EP[t] + self.baseload[t] <= self.max_connection_power

    def _add_battery_constraints(self) -> None:
        """Adds constraints related to the battery."""
        # Battery charge/discharge
        for t in self.T:
            self.prob += self.P_B_pos[t] <= battery_step_size * self.Q / 2
            self.prob += self.P_B_neg[t] <= battery_step_size * self.Q / 2

        # State of charge battery
        for t in self.T:
            self.prob += self.SoC[t + 1] == self.SoC[t] + 0.25 * self.P_B_pos[t] * (
                1 - battery_loss_charge
            ) - 0.25 * self.P_B_neg[t] / (1 - battery_loss_discharge)
            self.prob += self.SoC[t] <= battery_step_size * self.Q

        self.prob += self.SoC[0] == self.SoC[self.T.stop]

        if self.battery_size is not None:
            self.prob += self.battery_size / battery_step_size == self.Q

    def _add_vehicle_power_constraints(self) -> None:
        """Add constraints related to the vehicle power."""
        # Cannot charge outside the arrival and departure times

        # Vehicle energy demand
        for d in range(days_in_current_year):
            self.prob += (
                lpSum(
                    self.P_CP[t] * 0.25
                    for t in range(self.time_day_offset + int(d * 96), self.time_day_offset + int((d + 1) * 96))
                    if self.nr_of_vehicles_present[t] >= 1
                )
                == self.E_Vdem
            )

        # Power bounds with binary activation
        for t in self.T:
            self.prob += self.P_min * self.nr_of_vehicles_present[t] * self.phi[t] <= self.P_CP[t]
            self.prob += self.P_CP[t] <= self.P_max * self.nr_of_vehicles_present[t] * self.phi[t]

    def _add_energy_pod_constraints(self) -> None:
        """Add constraints for the EnergyPod power, which is the sum of the vehicle power and battery power."""
        for t in self.T:
            self.prob += self.P_EP[t] == self.P_CP[t] + self.P_B_pos[t] - self.P_B_neg[t]

    def _add_cost_constraints(self) -> None:
        """Adds constraints related to the cost functions for cp power, battery and penalty."""
        self.prob += self.C_EP == lpSum(self.P_EP[t] * self.c_t[t] * 0.25 for t in self.T)  # noqa: SIM300

        if self.max_connection_power != min(self.contract_connection_power):
            self.prob += self.C_pen == lpSum(self.P_pen[t] * self.pen * 0.25 for t in self.T)

    def _add_minimization_problem(self) -> None:
        """Adds objective function for the minimization problem."""
        if self.max_connection_power != min(self.contract_connection_power):
            self.prob += self.C_EP + self.C_pen + battery_price_per_kwh * battery_step_size * self.Q
        else:
            self.prob += self.C_EP + battery_price_per_kwh * battery_step_size * self.Q

    def _calculate_energy_cost_results(self) -> EnergyCostsYearWithEP:
        """Calculates the energy costs corresponding to the optimization result."""
        ep_energy_usage_year = np.array(
            [
                [value(self.P_EP[t]) * 0.25 for t in range(day * 96, (day + 1) * 96)]
                for day in range(days_in_current_year)
            ]
        )
        energy_costs_day = ep_energy_usage_year * np.array(
            [[self.c_t[t] for t in range(day * 96, (day + 1) * 96)] for day in range(days_in_current_year)]
        )

        energy_price_markup_costs = np.round(np.sum(ep_energy_usage_year * energy_price_markup), 2)
        energy_tax_costs = calculate_energy_tax(yearly_energy_consumption=np.sum(ep_energy_usage_year))

        total_energy_costs_day = np.round(np.sum(energy_costs_day, axis=1), 2).tolist()
        total_energy_costs = sum(total_energy_costs_day)

        return EnergyCostsYearWithEP(
            energy_costs_day=total_energy_costs_day,
            total_yearly_energy_costs=total_energy_costs,
            energy_price_markup_costs=energy_price_markup_costs,
            energy_tax_costs=energy_tax_costs,
        )

    def _calculate_capacity_exceedances(self) -> tuple[float, list[int], list[float]]:
        """Calculates the number of capacity exceedances, the exceeded power and costs for exceeding the capacity."""
        if self.max_connection_power != min(self.contract_connection_power):
            costs_capacity_exceedances_next_day = (
                sum(
                    [
                        value(self.P_pen[t]) * self.pen * 0.25
                        for t in range(self.T.stop - self.t_ch_next_day, self.T.stop)
                    ]
                )
                if self.overnight
                else 0
            )
            total_costs_capacity_exceedances = value(self.C_pen) - costs_capacity_exceedances_next_day

            nr_capacity_exc = np.array(
                [
                    [value(self.P_pen[t]) > 0 for t in range(day * 96, (day + 1) * 96)]
                    for day in range(days_in_current_year)
                ]
            )
            nr_capacity_exc_day = np.sum(nr_capacity_exc, axis=1).tolist()

            power_capacity_exc = np.array(
                [[value(self.P_pen[t]) for t in range(day * 96, (day + 1) * 96)] for day in range(days_in_current_year)]
            )
            power_capacity_exc_day = np.round(np.sum(power_capacity_exc, axis=1) / 4, 2).tolist()
        else:
            total_costs_capacity_exceedances = 0
            nr_capacity_exc_day = np.zeros(days_in_current_year).tolist()
            power_capacity_exc_day = np.zeros(days_in_current_year).tolist()

        return total_costs_capacity_exceedances, nr_capacity_exc_day, power_capacity_exc_day

    def calculate_optimization_results(self) -> OptimizationResults:
        """Minimizes the cost of charging vehicles using the battery."""
        # Try to solve the optimization problem
        if self.prob.solve(HiGHS(msg=False, gapRel=0.1, mip=True)) != 1:
            raise OptimizationError

        # Energy costs
        energy_costs_year = self._calculate_energy_cost_results()

        # Capacity exceedances
        total_costs_capacity_exceedances, nr_capacity_exc_day, power_capacity_exc_day = (
            self._calculate_capacity_exceedances()
        )

        # Results for charge point power from optimization problem
        T_end = self.T.stop - (self.t_ch_next_day) if self.overnight else self.T.stop
        cps_total = np.array([value(self.P_CP[t]) or 0 for t in range(T_end)])

        # Results for battery charge and discharge power from optimization problem
        battery_power_results = np.array([value(self.P_B_pos[t]) - value(self.P_B_neg[t]) for t in range(T_end)])
        datetime_results = [self.datetimes[i] for i in range(T_end)]

        optimized_energy = [
            OptimizedEnergy(
                datetime=datetime_results[i],
                cp_power=cps_total[i],
                battery_power=battery_power_results[i],
            )
            for i in range(T_end)
        ]

        # Battery capacity from optimization problem
        optimal_battery_capacity = int(value(self.Q) * battery_step_size)

        return OptimizationResults(
            optimized_energy=optimized_energy,
            battery_capacity=optimal_battery_capacity,
            total_energy_costs=energy_costs_year.total_yearly_energy_costs,
            total_energy_costs_day=energy_costs_year.energy_costs_day,
            energy_price_markup_costs=energy_costs_year.energy_price_markup_costs,
            energy_tax_costs=energy_costs_year.energy_tax_costs,
            total_costs_capacity_exceedances=total_costs_capacity_exceedances,
            nr_capacity_exceedances_day=nr_capacity_exc_day,
            power_capacity_exceedances_day=power_capacity_exc_day,
        )
