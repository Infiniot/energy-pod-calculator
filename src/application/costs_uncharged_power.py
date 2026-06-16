"""Contains functions to calculate the costs for the uncharged power."""

from src.config import fast_charging_tariff


def calculate_costs_uncharged_power(uncharged_power: list[float]) -> float:
    """Calculates the yearly costs for the uncharged power.

    Args:
        uncharged_power: List of uncharged power for each quarter over a year.
    """
    total_uncharged_power = sum(uncharged_power)
    return round(total_uncharged_power * fast_charging_tariff, 2)
