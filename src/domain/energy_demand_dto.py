"""Contains the pydantic models related to energy demand endpoint."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.domain.vehicle_info import VehicleInfoDTO


class EnergyDemandDTO(BaseModel):
    """A pydantic model representing the input for the energy demand feasibility endpoint as DTO."""

    model_config = ConfigDict(from_attributes=True)

    vehicle_info: VehicleInfoDTO
    arrival_time: str
    departure_time: str
    charge_point_power: str


class EnergyDemandResultDTO(BaseModel):
    """A pydantic model representing the output for the energy demand feasibility endpoint as DTO."""

    model_config = ConfigDict(from_attributes=True)

    vans: bool
    boxtrucks: bool
    semitrailertrucks: bool
