"""Contains the pydantic models related to the energy prices."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict


class EnergyPrice(BaseModel):
    """A pydantic model representing the energy price from Entsoe."""

    model_config = ConfigDict(from_attributes=True)

    datetime: str
    price: float


class ScaledEnergyPrice(BaseModel):
    """A pydantic model representing the scaled energy price from Entsoe."""

    model_config = ConfigDict(from_attributes=True)

    datetime: datetime
    price: float
