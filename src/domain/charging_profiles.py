"""Contains the pydantic models related to charging profiles."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict

from src.domain.connection_power import ConnectionPower


class ChargingProfile(BaseModel):
    """A pydantic model representing a charging profile entry."""

    model_config = ConfigDict(from_attributes=True)

    datetime: datetime
    power: float


class ChargingProfileDTO(BaseModel):
    """A pydantic model representing the input for charging profiles endpoint as DTO."""

    model_config = ConfigDict(from_attributes=True)

    arrival_time: str
    departure_time: str
    connection_power: list[ConnectionPower]


class ChargingProfileResults(BaseModel):
    """A pydantic model representing the output for the charging profiles without EP."""

    model_config = ConfigDict(from_attributes=True)

    charging_profiles: list[ChargingProfile]
    uncharged_power: list[float]
    vehicles_not_fully_charged: list[int]
    worst_day_uncharged_power: datetime
    worst_day_vehicles: datetime
