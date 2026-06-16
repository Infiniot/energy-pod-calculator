"""Unit tests for application.energy_costs.calculate_energy_costs using AAA pattern.

Each test includes a docstring and returns None.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from src.application.energy_costs import (
    calculate_energy_costs_year_without_ep,
    calculate_energy_tax,
    calculate_highest_energy_costs_savings,
)
from src.config import first_day_of_year
from src.domain.energy_costs import HighestEnergyCostsSavings
from src.domain.without_energy_pod import EnergyWithoutEP


@patch("src.application.energy_prices.read_energy_prices_from_csv")
def test_calculate_energy_costs_year_without_ep(mock_read: MagicMock) -> None:
    """Arrange: energy consumption year with known values.

    Act: call calculate_energy_costs_year with the energy consumption year.
    Assert: returns expected energy costs for a year.
    """
    # Arrange
    # mock csv read to return comprehensable data points
    now = datetime.now(tz=UTC).replace(month=1, day=1)
    days = 365 + (now.year % 4 == 0)
    start_dates = pd.date_range(start=datetime.strftime(now, "%Y-%m-%d"), periods=96 * days, freq="15min", tz=UTC)

    prices = [0.1] * days * 96
    mock_read.return_value = pd.DataFrame({"Start date": start_dates, "Day-ahead Price (EUR/MWh)": prices})

    energypods = (
        [
            EnergyWithoutEP(
                datetime=datetime(now.year, 1, 1, 0, 0, tzinfo=ZoneInfo("Europe/Amsterdam")).strftime("%m/%d/%Y %H:%M"),
                baseload_power=5.0,
                contract_power=55,
                charge_point_power=25.0,
            )
            for _ in range(96)
        ]
        + [
            EnergyWithoutEP(
                datetime=datetime(now.year, 1, 2, 0, 0, tzinfo=ZoneInfo("Europe/Amsterdam")).strftime("%m/%d/%Y %H:%M"),
                baseload_power=5.0,
                contract_power=55,
                charge_point_power=100.0,
            )
            for _ in range(96)
        ]
        + [
            EnergyWithoutEP(
                datetime=(
                    datetime(now.year, 1, 3, 0, 0, tzinfo=ZoneInfo("Europe/Amsterdam")) + timedelta(minutes=i * 15)
                ).strftime("%m/%d/%Y %H:%M"),
                baseload_power=5.0,
                contract_power=55,
                charge_point_power=25.0,
            )
            for i in range((days - 2) * 96)
        ]
    )
    expected_total_costs_day = np.array([0.24, 0.96] + [0.24] * (days - 2)) * 0.25
    expected_worst_day = datetime(now.year, 1, 2, 0, 0, tzinfo=ZoneInfo("Europe/Amsterdam"))
    expected_ere_reduction_costs = 22080.0
    expected_energy_price_markup_costs = 552.0
    expected_energy_tax_costs = 10396.74

    # Act
    result = calculate_energy_costs_year_without_ep(energy_consumption_year=energypods)

    # Assert
    mock_read.assert_called_once()
    assert hasattr(result, "energy_costs_day")
    assert isinstance(result.energy_costs_day, list)
    assert hasattr(result, "worst_day_energy_costs")
    assert isinstance(result.worst_day_energy_costs, datetime)
    assert hasattr(result, "ere_reduction_costs")
    assert isinstance(result.ere_reduction_costs, float)
    assert hasattr(result, "energy_price_markup_costs")
    assert isinstance(result.energy_price_markup_costs, float)
    assert hasattr(result, "energy_tax_costs")
    assert isinstance(result.energy_tax_costs, float)

    assert len(result.energy_costs_day) == len(expected_total_costs_day)
    assert np.all(result.energy_costs_day == expected_total_costs_day)
    assert result.worst_day_energy_costs == expected_worst_day
    assert result.ere_reduction_costs == expected_ere_reduction_costs
    assert result.energy_price_markup_costs == expected_energy_price_markup_costs
    assert result.energy_tax_costs == expected_energy_tax_costs


def test_calculate_highest_energy_costs_savings() -> None:
    """Arrange: Prepare list with energy costs per day for scenario with and without energypod.

    Act: Call calculate_highest_energy_costs_savings.
    Assert: Returned object has correct attributes and values.
    """
    # Arrange
    mock_energy_costs_no_ep = [5.0] * 200 + [300.0] + [5.0] * 164
    mock_energy_costs_ep = [7.0] * 365

    # Act
    result = calculate_highest_energy_costs_savings(mock_energy_costs_no_ep, mock_energy_costs_ep)

    expected_result = HighestEnergyCostsSavings(
        datetime=first_day_of_year + timedelta(days=200),
        absolute_savings=293.0,
        energy_costs_no_ep=300.0,
        energy_costs_ep=7.0,
    )

    # Assert
    assert hasattr(result, "datetime")
    assert hasattr(result, "absolute_savings")
    assert hasattr(result, "energy_costs_no_ep")
    assert hasattr(result, "energy_costs_ep")

    assert result.datetime == expected_result.datetime
    assert result.absolute_savings == expected_result.absolute_savings
    assert result.energy_costs_ep == expected_result.energy_costs_ep
    assert result.energy_costs_no_ep == expected_result.energy_costs_no_ep


def test_calculate_energy_tax() -> None:
    """Arrange: Prepare the total yearly energy consumption.

    Act: Call calculate_energy_tax.
    Assert: Returned object has the correct type and value.
    """
    # Arrange
    mock_yearly_energy_consumption = 60000

    # Act
    result = calculate_energy_tax(yearly_energy_consumption=mock_yearly_energy_consumption)
    expected_result = 4177.0

    # Assert
    assert isinstance(result, float)
    assert result == expected_result
