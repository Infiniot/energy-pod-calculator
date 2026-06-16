"""The router containing the endpoint to calculate the payback time."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.payback_time import calculate_payback_time

payback_time_router = APIRouter(prefix="/payback_time", tags=["payback time"])


@payback_time_router.get("/")
def get_payback_time(
    yearly_savings_ep: float,
    investment_costs_no_ep: float,
    investment_costs_ep: float,
) -> float:
    """Retrieves the payback time for the scenario with EnergyPod compared to the scenario without EnergyPod.

    Args:
        yearly_savings_ep: The yearly savings for the scenario with EnergyPod.
        investment_costs_no_ep: The total investment costs for the scenario without EnergyPod.
        investment_costs_ep: The total investment costs for the scenario with EnergyPod.
    """
    return calculate_payback_time(yearly_savings_ep, investment_costs_no_ep, investment_costs_ep)
