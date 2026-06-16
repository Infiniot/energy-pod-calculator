"""The router containing the endpoints for the day with the highest energy cost savings."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.energy_costs import calculate_highest_energy_costs_savings
from src.domain.energy_costs import EnergyCostsDTO, HighestEnergyCostsSavings

energy_costs_savings_router = APIRouter(prefix="/highest_energy_costs_savings", tags=["highest energy costs savings"])


@energy_costs_savings_router.post("/")
def get_highest_energy_costs_savings(energy_costs_dto: EnergyCostsDTO) -> HighestEnergyCostsSavings:
    """Retrieves the day with the highest energy costs savings with EnergyPod."""
    return calculate_highest_energy_costs_savings(energy_costs_dto.energy_costs_no_ep, energy_costs_dto.energy_costs_ep)
