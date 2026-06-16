"""Contains the pydantic models related to optimized charging profiles and battery."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict


class OptimizedEnergy(BaseModel):
    """A pydantic model representing the optimized EnergyPod power consumption."""

    model_config = ConfigDict(from_attributes=True)

    datetime: datetime
    cp_power: float
    battery_power: float


class OptimizationResults(BaseModel):
    """A pydantic model representing the EnergyPod power and costs resulting from the optimization."""

    model_config = ConfigDict(from_attributes=True)

    optimized_energy: list[OptimizedEnergy]
    battery_capacity: int
    total_energy_costs: float
    total_energy_costs_day: list[float]
    energy_price_markup_costs: float
    energy_tax_costs: float
    total_costs_capacity_exceedances: float
    nr_capacity_exceedances_day: list[int]
    power_capacity_exceedances_day: list[float]
