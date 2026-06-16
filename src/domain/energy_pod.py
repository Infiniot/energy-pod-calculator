"""Contains the pydantic models related to charging profiles and battery."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict


class EnergyPod(BaseModel):
    """A pydantic model representing an EnergyPod power consumption entry."""

    model_config = ConfigDict(from_attributes=True)

    datetime: str
    baseload_power: float
    contract_power: float
    charge_point_power: float
    battery_charge_power: float
    battery_discharge_power: float


class EnergyPodResults(BaseModel):
    """A pydantic model representing the EnergyPod power results of the optimization."""

    model_config = ConfigDict(from_attributes=True)

    consumption: list[EnergyPod]
    battery_results: BatteryResults
    yearly_energy_costs: list[float]
    total_yearly_energy_costs: float
    energy_price_markup_costs: float
    energy_tax_costs: float
    ere_reduction_costs: float
    yearly_costs_capacity_exceedances: float
    investment_costs_cp: float
    nr_capacity_exceedances_year: list[int]
    power_capacity_exceedances_year: list[float]
    worst_day_energy_costs: datetime
    worst_day_nr_exceedances: datetime
    worst_day_power_exceedances: datetime


class BatteryResults(BaseModel):
    """A pydantic model representing the battery results of the EnergyPod optimization."""

    model_config = ConfigDict(from_attributes=True)

    capacity: int
    power: int
    cost: float
