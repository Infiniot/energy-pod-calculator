"""Contains the pydantic models related to the total energy usage."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict


class EnergyWithoutEP(BaseModel):
    """A pydantic model representing an energy usage entry without EnergyPod."""

    model_config = ConfigDict(from_attributes=True)

    datetime: str
    baseload_power: float
    contract_power: float
    charge_point_power: float


class ResultWithoutEP(BaseModel):
    """A pydantic model representing the results without EnergyPod."""

    model_config = ConfigDict(from_attributes=True)

    consumption: list[EnergyWithoutEP]
    total_yearly_energy_costs: float
    yearly_costs: list[float]
    energy_price_markup_costs: float
    energy_tax_costs: float
    ere_reduction_costs: float
    nr_capacity_exceedances_year: list[int]
    power_capacity_exceedances_year: list[float]
    yearly_costs_capacity_exceedances: float
    uncharged_power: list[float]
    yearly_costs_uncharged_power: float
    vehicles_not_fully_charged: list[int]
    investment_costs: float
    worst_day_uncharged_power: datetime
    worst_day_vehicles: datetime
    worst_day_energy_costs: datetime


class EnergyResultsWithoutEP(BaseModel):
    """A pydantic model representing the total output for the charging profiles without EP."""

    model_config = ConfigDict(from_attributes=True)

    energy_consumption: list[EnergyWithoutEP]
    uncharged_power: list[float]
    vehicles_not_fully_charged: list[int]
    worst_day_uncharged_power: datetime
    worst_day_vehicles: datetime
