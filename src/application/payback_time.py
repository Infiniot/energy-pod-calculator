"""Contains functions to calculate the payback time for the scenario with EnergyPod."""

from __future__ import annotations


def calculate_payback_time(
    yearly_savings_ep: float, investment_costs_no_ep: float, investment_costs_ep: float
) -> float:
    """Calculates the payback time for purchasing the EnergyPod, compared to the scenario without EnergyPod."""
    return round((investment_costs_ep - investment_costs_no_ep) / (yearly_savings_ep))
