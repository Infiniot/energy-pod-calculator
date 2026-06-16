"""Contains function to calculate charging profiles."""

from __future__ import annotations

from datetime import datetime, timedelta
from functools import reduce

import numpy as np

from src.config import days_in_current_year, first_day_of_year
from src.domain.baseload_profile import BaseloadProfile
from src.domain.charging_profiles import ChargingProfile, ChargingProfileDTO, ChargingProfileResults
from src.domain.vehicle_info import (
    VehicleType,
    VehicleTypeInfo,
)


class Vehicle:
    """Class to store all variables related to a single vehicle."""

    def __init__(
        self,
        vehicle_type: VehicleType,
        power_usage: float,
        annual_km: int,
        arrival_time: datetime,
        departure_time: datetime,
    ) -> None:
        """Initializes a vehicle class."""
        self.vehicle_type = vehicle_type
        self.power_usage = power_usage
        self.annual_km = annual_km
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.current_capacity = 0.0
        self.is_charging = False

        # Determine battery capacity
        self.calculate_max_capacity()

    def calculate_max_capacity(self) -> None:
        """Determines the maximum capacity of the vehicles battery."""
        self.max_capacity = round(self.annual_km / 365 * self.power_usage)

    def update_is_charging(self) -> None:
        """Updates the state of charge of the vehicle."""
        self.is_charging = not self.is_charging


class ChargingProfilesWithoutEP:
    """Class that calculates the charging profiles for the scenario without EnergyPod."""

    def __init__(
        self,
        charging_profiles_input: ChargingProfileDTO,
        vehicle_info: list[VehicleTypeInfo],
        baseload_profiles: list[BaseloadProfile],
        charge_point_power: int,
    ) -> None:
        """Initializes the ChargingProfilesWithoutEP class."""
        self.arrival_time = charging_profiles_input.arrival_time
        self.departure_time = charging_profiles_input.departure_time
        self.connection_power = charging_profiles_input.connection_power
        self.vehicle_info = vehicle_info
        self.baseload_profiles = baseload_profiles
        self.charge_point_power = charge_point_power
        self.total_nr_of_vehicles = np.sum([info.nr_of_vehicles for info in self.vehicle_info])
        self.quarters = np.array([0, 15, 30, 45, 60])
        self.hour = 60

    def _round_to_nearest_quarter(
        self, t: datetime, arrival_datetime_day_nr: datetime, departure_datetime_day_nr: datetime, *, arrival: bool
    ) -> datetime:
        """Round datetime to nearest quarter."""
        nearest_quarter = self.quarters[np.argmin(np.abs(self.quarters - t.minute))]

        if arrival and (self.overnight_time > 0) and (t < (departure_datetime_day_nr - timedelta(days=1))):
            t = departure_datetime_day_nr - timedelta(days=1)
        elif arrival and (self.overnight_time == 0) and (t.day < arrival_datetime_day_nr.day):
            t = arrival_datetime_day_nr.replace(hour=0, minute=0, second=0, microsecond=0)
        elif arrival and (t > departure_datetime_day_nr):
            t = departure_datetime_day_nr
        elif (not arrival) and (self.overnight_time > 0) and (t > (arrival_datetime_day_nr + timedelta(days=1))):
            t = arrival_datetime_day_nr + timedelta(days=1)
        elif (not arrival) and (self.overnight_time == 0) and (t.day > departure_datetime_day_nr.day):
            t = departure_datetime_day_nr.replace(hour=23, minute=45, second=0, microsecond=0)
        elif (not arrival) and t < arrival_datetime_day_nr:
            t = arrival_datetime_day_nr
        elif nearest_quarter == self.hour:
            t = t.replace(minute=0)
            t += timedelta(hours=1)
        else:
            t = t.replace(minute=nearest_quarter)

        return t

    def _rounded_stoch_times(
        self, arrival_datetime_day_nr: datetime, departure_datetime_day_nr: datetime, *, arrival: bool
    ) -> np.ndarray:
        """Determines stochastic times rounded to nearest quarter for all vehicles for one day."""
        np_generator = np.random.default_rng()
        stoch_component = np.astype(np_generator.normal(loc=0, scale=30, size=self.total_nr_of_vehicles), int)

        start_date_stoch_times = arrival_datetime_day_nr if arrival else departure_datetime_day_nr
        stoch_times = np.array([start_date_stoch_times + timedelta(minutes=int(t_min)) for t_min in stoch_component])
        return np.array(
            [
                self._round_to_nearest_quarter(t, arrival_datetime_day_nr, departure_datetime_day_nr, arrival=arrival)
                for t in stoch_times
            ]
        )

    def _stochastic_arrival_and_departure_times_day(self, day_nr: int) -> tuple[np.ndarray, np.ndarray]:
        """Determines stochastic arrival and departure times for all vehicles for one day."""
        arrival_datetime_day_nr = self.arrival_datetime + timedelta(days=day_nr)
        departure_datetime_day_nr = self.departure_datetime + timedelta(days=day_nr)

        rounded_stoch_arr_times = self._rounded_stoch_times(
            arrival_datetime_day_nr, departure_datetime_day_nr, arrival=True
        )

        rounded_stoch_dep_times = self._rounded_stoch_times(
            arrival_datetime_day_nr, departure_datetime_day_nr, arrival=False
        )

        return rounded_stoch_arr_times, rounded_stoch_dep_times

    def _create_vehicles_day(self, day_nr: int) -> list[Vehicle]:
        """Creates a list of all vehicles and their characteristics for one day."""
        stoch_arrival_times, stoch_departure_times = self._stochastic_arrival_and_departure_times_day(day_nr)

        vehicle_count = 0

        vehicles: list[Vehicle] = []
        for vehicle_type in VehicleType:
            vehicle_type_info = next(info for info in self.vehicle_info if info.vehicle_type == vehicle_type)
            for _ in range(vehicle_type_info.nr_of_vehicles):
                vehicles.append(
                    Vehicle(
                        vehicle_type=vehicle_type,
                        power_usage=vehicle_type_info.power_usage,
                        annual_km=vehicle_type_info.annual_km,
                        arrival_time=stoch_arrival_times[vehicle_count],
                        departure_time=stoch_departure_times[vehicle_count],
                    )
                )

                vehicle_count += 1

        return vehicles

    def _update_active_charging_sessions_t(self, t: int) -> None:
        """Determines the number of active charging sessions at time t."""
        for v in self.vehicles:
            if (
                (self.datetimes[t] >= v.arrival_time)
                and (self.datetimes[t] <= v.departure_time)
                and (v.current_capacity < v.max_capacity)
            ):
                self.active_charging_sessions[t] += 1
                v.update_is_charging()

    def _update_avg_charging_power_t(self, t: int) -> None:
        """Determines the average charging power for a single vehicle for time t."""
        if self.active_charging_sessions[t] > 0:
            self.avg_charging_power[t] = self.remaining_connection_power[t] / self.active_charging_sessions[t]

    def _update_total_charging_power_t(self, t: int) -> None:
        """Determines the total charging power over all charging sessions at time t.

        In addition, updates the current capacity for each vehicle at time t.
        """
        time_delta = 0.25

        for v in self.vehicles:
            if v.is_charging:
                v.update_is_charging()
                self.total_charging_power[t] += min(
                    self.avg_charging_power[t],
                    (v.max_capacity - v.current_capacity) / time_delta,
                    self.charge_point_power,
                )
                v.current_capacity += (
                    min(
                        self.avg_charging_power[t],
                        (v.max_capacity - v.current_capacity) / time_delta,
                        self.charge_point_power,
                    )
                    * time_delta
                )

    def _schedule_charging_vehicles_day(self, indices_day: np.ndarray) -> None:
        """Creates charging schedule for a single day."""
        for t in indices_day:
            # Determine the active charging sessions at time t
            self._update_active_charging_sessions_t(t)

            # Determine the average charging power per vehicle
            self._update_avg_charging_power_t(t)

            # Determine the total charging power used for all charging sessions at time t
            self._update_total_charging_power_t(t)

    def calculate_charging_profiles_without_ep(self) -> ChargingProfileResults:
        """Calculates the charging sessions over a year resulting from the input."""
        # Determine the current datetime
        start_datetime = first_day_of_year
        days = days_in_current_year

        # Set the arrival and departure datetimes
        self.arrival_datetime = start_datetime.replace(
            hour=int(self.arrival_time.split(":")[0]), minute=int(self.arrival_time.split(":")[1])
        )
        self.departure_datetime = start_datetime.replace(
            hour=int(self.departure_time.split(":")[0]), minute=int(self.departure_time.split(":")[1])
        )

        self.remaining_connection_power = np.array(
            [
                self.connection_power[i].power - self.baseload_profiles[i].power
                for i in range(len(self.baseload_profiles))
            ]
        )

        # If leap year, add extra day to remaining connection power
        if first_day_of_year.year % 4 == 0:
            self.remaining_connection_power = np.concat(
                [self.remaining_connection_power, self.remaining_connection_power[:96]]
            )

        # Determine the timewindow for charging
        self.overnight_time = 0
        if self.arrival_datetime and self.departure_datetime and (self.arrival_datetime > self.departure_datetime):
            self.departure_datetime = self.departure_datetime + timedelta(days=1)
            self.overnight_time = reduce(lambda x, y: x * 4 + y // 15, map(int, self.departure_time.split(":")))

        self.datetimes: np.ndarray = np.array(
            [start_datetime + timedelta(minutes=15 * t) for t in range(96 * days + self.overnight_time)]
        )

        self.active_charging_sessions: np.ndarray = np.zeros(96 * days + self.overnight_time, dtype=int)
        self.total_charging_power: np.ndarray = np.zeros(96 * days + self.overnight_time, dtype=float)
        self.avg_charging_power: np.ndarray = np.zeros(96 * days + self.overnight_time, dtype=float)

        datetimes_day = np.split(self.datetimes[self.overnight_time :], days)

        uncharged_power = []
        vehicles_not_fully_charged = []

        for day_nr in range(len(datetimes_day)):
            _, indices_day, _ = np.intersect1d(self.datetimes, datetimes_day[day_nr], return_indices=True)
            self.vehicles = self._create_vehicles_day(day_nr)

            self._schedule_charging_vehicles_day(indices_day)

            uncharged_power.append(
                round(float(np.sum([v.max_capacity - v.current_capacity for v in self.vehicles])), 2)
            )
            vehicles_not_fully_charged.append(np.sum([v.max_capacity - v.current_capacity > 0 for v in self.vehicles]))

        worst_day_uncharged_power = start_datetime + timedelta(days=int(np.argmax(uncharged_power)))
        worst_day_vehicles = start_datetime + timedelta(days=int(np.argmax(vehicles_not_fully_charged)))

        return ChargingProfileResults(
            charging_profiles=[
                ChargingProfile(
                    datetime=self.datetimes[i],
                    power=round(self.total_charging_power[i], 2),
                )
                for i in range(96 * days)
            ],
            uncharged_power=uncharged_power,
            vehicles_not_fully_charged=vehicles_not_fully_charged,
            worst_day_uncharged_power=worst_day_uncharged_power,
            worst_day_vehicles=worst_day_vehicles,
        )
