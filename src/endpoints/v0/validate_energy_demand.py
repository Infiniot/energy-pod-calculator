"""Router containing the endpoint to check if the energy demand is feasible within the charging window."""

from __future__ import annotations

from fastapi import APIRouter

from src.domain.energy_demand_dto import EnergyDemandDTO, EnergyDemandResultDTO
from src.utils.time_frame import calculate_indices_arrival_departure_time

validate_energy_demand_router = APIRouter(prefix="/validate_energy_demand", tags=["validate energy demand"])


@validate_energy_demand_router.post("/")
def calculate_energy_demand_feasibility(energy_demand_input: EnergyDemandDTO) -> EnergyDemandResultDTO:
    """Checks if the energy demand is feasible."""
    arrival_index, departure_index = calculate_indices_arrival_departure_time(
        energy_demand_input.arrival_time, energy_demand_input.departure_time
    )
    charge_point_power = int(energy_demand_input.charge_point_power.split(" ")[0])
    time_frame_length = departure_index - arrival_index
    available_energy_per_vehicle = time_frame_length * charge_point_power / 4

    feasible = {}
    for vehicle_type in energy_demand_input.vehicle_info.get_vehicle_infos():
        if vehicle_type.nr_of_vehicles == 0:
            feasible[vehicle_type.vehicle_type.value] = True
            continue
        energy_demand = vehicle_type.calculate_energy_demand()
        if energy_demand > available_energy_per_vehicle:
            feasible[vehicle_type.vehicle_type.value] = False
        else:
            feasible[vehicle_type.vehicle_type.value] = True

    return EnergyDemandResultDTO(**feasible)
