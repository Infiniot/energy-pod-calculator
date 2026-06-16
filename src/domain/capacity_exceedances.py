"""Contains the pydantic models related to the capacity exceedances."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CapacityExceedancesNoEP(BaseModel):
    """A pydantic model representing the capacity exceedances."""

    model_config = ConfigDict(from_attributes=True)

    nr_capacity_exceedances_year: list[int]
    power_capacity_exceedances_year: list[float]
    yearly_costs_capacity_exceedances: float
