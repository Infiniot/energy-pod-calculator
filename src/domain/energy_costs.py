"""Contains the pydantic models related to the energy costs."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict


class EnergyCostsYearWithoutEP(BaseModel):
    """A pydantic model representing the total energy costs of power consumption without EnergyPod over a year."""

    energy_costs_day: list[float]
    worst_day_energy_costs: datetime
    ere_reduction_costs: float
    energy_price_markup_costs: float
    energy_tax_costs: float


class EnergyCostsYearWithEP(BaseModel):
    """A pydantic model representing the total energy costs of power consumption with EnergyPod over a year."""

    energy_costs_day: list[float]
    total_yearly_energy_costs: float
    energy_price_markup_costs: float
    energy_tax_costs: float


class HighestEnergyCostsSavings(BaseModel):
    """A pydantic model representing the day with the highest energy costs savings."""

    model_config = ConfigDict(from_attributes=True)

    datetime: datetime
    absolute_savings: float
    energy_costs_no_ep: float
    energy_costs_ep: float


class EnergyCostsDTO(BaseModel):
    """A pydantic model representing the input for calculating the highest energy costs savings as DTO."""

    model_config = ConfigDict(from_attributes=True)

    energy_costs_no_ep: list[float]
    energy_costs_ep: list[float]
