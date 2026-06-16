"""Contains functions to calculate the yearly savings for the scenario with EnergyPod."""

from __future__ import annotations


def calculate_yearly_savings(yearly_costs_no_ep: float, yearly_costs_ep: float) -> float:
    """Calculates the yearly savings for the scenario with EnergyPod compared to the scenario without EnergyPod."""
    return round(yearly_costs_no_ep - yearly_costs_ep, 2)
