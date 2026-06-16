"""Contains the pydantic models related to vehicle information."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class VehicleType(Enum):
    """Enum types for vehicle types."""

    VAN = "vans"
    BOXTRUCK = "boxtrucks"
    SEMITRAILERTRUCK = "semitrailertrucks"


class VehicleTypeInfo(BaseModel):
    """A pydantic model representing the vehicle information of a vehicle type."""

    model_config = ConfigDict(from_attributes=True)

    vehicle_type: VehicleType
    nr_of_vehicles: int
    power_usage: float
    annual_km: int

    def calculate_energy_demand(self) -> float:
        """Determines the energy demand of one vehicle."""
        return round(self.annual_km / 365 * self.power_usage)


class VehicleTypeInfoDTO(BaseModel):
    """A pydantic model representing the input for a vehicle type information as DTO."""

    model_config = ConfigDict(from_attributes=True)

    nr_of_vehicles: int
    power_usage: float
    annual_km: int

    def calculate_energy_demand(self) -> float:
        """Determines the energy demand of one vehicle."""
        return round(self.annual_km / 365 * self.power_usage)

    def calculate_total_energy_demand_vehicles(self) -> float:
        """Determines the total energy demand for all vehicles for a single day."""
        return self.nr_of_vehicles * self.calculate_energy_demand()


class VehicleInfoDTO(BaseModel):
    """A pydantic model representing the input for vehicle information as DTO."""

    model_config = ConfigDict(from_attributes=True)

    vans: VehicleTypeInfoDTO
    boxtrucks: VehicleTypeInfoDTO
    semitrailertrucks: VehicleTypeInfoDTO

    def get_vehicle_infos(self) -> list[VehicleTypeInfo]:
        """Creates a list of all vehicle type information."""
        return [
            VehicleTypeInfo(vehicle_type=VehicleType.VAN, **self.vans.model_dump()),
            VehicleTypeInfo(vehicle_type=VehicleType.BOXTRUCK, **self.boxtrucks.model_dump()),
            VehicleTypeInfo(vehicle_type=VehicleType.SEMITRAILERTRUCK, **self.semitrailertrucks.model_dump()),
        ]

    def get_total_energy_demand_vehicle_types(self) -> float:
        """Determines the total energy demand for all vehicle types for a single day."""
        return (
            self.vans.calculate_total_energy_demand_vehicles()
            + self.boxtrucks.calculate_total_energy_demand_vehicles()
            + self.semitrailertrucks.calculate_total_energy_demand_vehicles()
        )

    def get_total_nr_of_vehicles(self) -> int:
        """Calculates the total number of vehicles for all vehicle types."""
        return self.vans.nr_of_vehicles + self.boxtrucks.nr_of_vehicles + self.semitrailertrucks.nr_of_vehicles
