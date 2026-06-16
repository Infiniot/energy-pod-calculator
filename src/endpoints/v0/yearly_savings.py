"""The router containing all the endpoint for calculating the yearly savings with an EnergyPod."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.yearly_savings import calculate_yearly_savings

yearly_savings_router = APIRouter(prefix="/yearly_savings", tags=["yearly savings"])


@yearly_savings_router.get("/")
def get_yearly_savings(yearly_costs_no_ep: float, yearly_costs_ep: float) -> float:
    """Retrieves the yearly savings for the scenario with EnergyPod.

    Args:
        yearly_costs_no_ep: Total yearly costs for the scenario without EnergyPod.
        yearly_costs_ep: Total yearly costs for the scenario with EnergyPod.
    """
    return calculate_yearly_savings(yearly_costs_no_ep, yearly_costs_ep)
